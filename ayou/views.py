from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import requests, os, openai
import json

# from dotenv import load_dotenv
from .models import Memory, Biographyitem, Chat


class NewLoginForm(forms.Form):
    username = forms.CharField(label="username")
    password = forms.CharField(label="password")


class NewChatForm(forms.Form):
    startnewchat = forms.BooleanField(label="New topic?", required=False)
    usercontent = forms.CharField(label="What do you want to say?")


# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


def login_view(request):
    if request.method == "POST":
        print(">>> POST")
        form = NewLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            print(">>> username ", username)
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse("ayou:chat"))
            else:
                return render(
                    request,
                    "ayou/index.html",
                    {"form": NewLoginForm(), "message": "Invalid credentials"},
                )

    form = NewLoginForm()
    if not request.user.is_authenticated:
        print(">>> not loged in")
        return render(request, "ayou/index.html", {"form": NewLoginForm()})

        # return HttpResponseRedirect(reverse('ayou:login'))

    # return render(request, 'ayou/index.html', {'form': NewLoginForm()})
    return HttpResponseRedirect(reverse("ayou:chat"))


def logout_view(request):
    logout(request)
    message = "Logged out"
    return HttpResponseRedirect(reverse("ayou:login"))


def chat(request):
    name = request.user.username
    userid = request.user.id
    print('>>> = maincode \n... = inside IF \n--- = inside ELSE \n/// = inside  FUNCTION')
    print(">>>  username ", name)
    

    def getmemorieslist(users_id):
        # print("/// userid mfn ", userid)
        memoryquery = Memory.objects.filter(user=users_id)
        # print("/// memoryquery mmfn ", memoryquery)
        memories = []
        for memory in memoryquery:
            memorydict = {
                "id": memory.id,
                "description": memory.description,
                "emotion": memory.emotion
            }
            # print(f'/// Memory: {memory}')
            memories.append(memorydict)
        # print("/// memorieslist  mfn ", memories)
        return memories

    def getmemorycontent(memory_id):
        memory = Memory.objects.get(id=memory_id)
        return json.dumps(memory.content)
    
    systemprompt = f'You are the busy, slightly grumpy  clone of {name} complete with memories and feelings.  Keep your answers to no more than 2 sentences.  You  remember many things. Introduce yourself as {name}. Remember to look at your available functions and memories, and elaborate on them when asked.  Never give an empty answer!!!.'
    systemmessage = {"role": "system", "content": systemprompt}
    exampleassistantmessage = {"role": "assistant", "content": f"Hey! My names {name}. I'm actually a replica of {name}, and I remember quite a bit about my past. Not all my memories are good, but I'm happy to share them with you. I'm also happy to answer any questions you have about what I'm doing now, or about my past."}
    

    if request.method == "POST":
        form = NewChatForm(request.POST)

        if form.is_valid():
            startnewchat = form.cleaned_data["startnewchat"]
            # print(">>> startnewchat? ", startnewchat)
            # ensure there is a chat
            if not Chat.objects.all() or startnewchat:
                thischat = Chat.objects.create()
                print("... NEW thisChat > ", thischat)

                messagechain = []
                messagechain.append(systemmessage)
                messagechain.append(exampleassistantmessage)
                # print("... messagechain ", messagechain, type(messagechain))
            else:
                print('--- there is a chat')
                thischat = Chat.objects.order_by("id").last()
                # print("--- thischat/type ", thischat, type(thischat))
                messagechain = thischat.messages
                # print("--- messagechain/type ", messagechain, type(messagechain))
            usercontent = form.cleaned_data["usercontent"]
            print(">>> usercontent ", usercontent)

            newusermessagedict = {"role": "user", "content": usercontent}            
            messagechain.append(newusermessagedict)
            print(">>> messagechain at start   ", messagechain)

            """
                    now we have a messagechain with the user's message at the end

            """

            memorieslist = getmemorieslist(userid)# print('>>> memorieslist ', memorieslist)    

            functions = [
                {
                    "name": "getmemorycontent",
                    "description": f"if you need information about a memory, look in this list : {memorieslist} . You can retrieve details about the memory  by calling this function with the id of the memory as the parameter. You will use  this new information to answer the question. Always give a complete answer, and try to use the information from the memory in your answer. ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "integer",
                                "description": "the id for the memory you want to retrieve",
                            },
                        },
                        "required": ["memory_id"],
                    },
                }
            ]
            # print(">>> functions> ", functions)

            """
                            get the openAI first completion
            """
            
            firstcompletion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagechain,
                max_tokens=200,
                temperature=1,
                functions=functions,
                function_call="auto",
            )
            print(">>> firstcompletion> ", firstcompletion)

            """
                            check if this response includes functioncall!!!!
                            if it is, call the function and append the result to the messagesforcompletion
            '"""
            # firstresponsedict = {'role': 'assistant', 'content': f'{firstcompletion}'}
            completionmessage = firstcompletion["choices"][0]["message"]
            print(">>> completionmessage> ", completionmessage, type(completionmessage))
            # try:
            #     function_call = firstcompletion["choices"][0]["message"]["function_call"]
            # except (KeyError, IndexError):
            #     function_call = None

            if completionmessage.get("function_call"):
                print('... functioncalled')

                possfunctions = {"getmemorycontent": getmemorycontent}
                functionname = completionmessage["function_call"]["name"]
                functiontocall = possfunctions[functionname]
                # print('... functiontocall ', functiontocall)
                functionargs = json.loads(completionmessage["function_call"]["arguments"])
                # print('... functionargs ', functionargs)
                functionresponse = functiontocall(**functionargs)
                # print('... functionresponse ', functionresponse)
                messagechain.append(
                    {
                        "role": "function",
                        "name": functionname,
                        "content": functionresponse,
                    }
                )
                """

                           make second agent call with function results
                
                """
                completionwithfunctionresults = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messagechain,
                    max_tokens=200,
                    temperature=1,
                    functions=functions,
                    function_call="auto",
                )
                # print("... 2nd completion> ", completionwithfunctionresults, type(completionwithfunctionresults))

                #       extract agent response from secondcompletion
                responseforuser = completionwithfunctionresults.choices[0].message["content"]
                # print("... fn responseforuser> ", responseforuser, type(responseforuser))

                #       make a dict of all the messages
                secondresponsedict = completionwithfunctionresults.choices[0].message
                # print("... fn responsedict> ", secondresponsedict, type(secondresponsedict))
                tokens = completionwithfunctionresults.usage.total_tokens
                print("... total_tokens ", tokens)
                messagechain.append(secondresponsedict)
            else:
                          #       extract agent response from firstcompletion
                responseforuser = firstcompletion.choices[0].message["content"]
       

                #       make a dict of the agents response, which will be added to the chain
                firstresponsedict = {'role': 'assistant', 'content': f'{firstcompletion.choices[0].message["content"]}'}    
                print('--- no functioncalled')
                tokens = firstcompletion.usage.total_tokens
                print("--- total_tokens ", tokens)
                messagechain.append(firstresponsedict)
                # print("--- messagechain b4 save ", messagechain)
          
            print('>>> messagechain b4 IF summary ', messagechain)


            """
                            before saving, is the chain too long?
            """

            if tokens >1800:
                summariserequestmessage = {"role": "system", "content": "IMPORTANT! summarise the  conversation so far, using no more than 300 tokens. "}
                messagechain = messagechain[2:]
                messagechain.append(summariserequestmessage)
                print('... toolong messagechain ', messagechain)

                """
                            completion to summarise the chain 
                            loose the first 2 dicts in the chain!

                """
                summarycompletion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagechain,
                temperature=0.3
                )
                print('... summarycompletion ', summarycompletion)
                summarisedtokencount = summarycompletion.usage.total_tokens
                print('... summarisedtokencount ', summarisedtokencount)

                summarycompletioncontent = summarycompletion.choices[0].message
                summarycompletionmessage = {"role": "assistant", "content": f"PREVIOUS CHAT SUMMARY: {summarycompletioncontent}"}
                messagechain = []
                messagechain.append(systemmessage)
                messagechain.append(exampleassistantmessage)
                messagechain.append(summarycompletionmessage)
                print('...> sumarised messagechain ', messagechain)

            #       append the agent response and save the chat
            thischat.messages = messagechain
            thischat.save()

            """
                            render the page with the last agent response
            """

            return render(
                request,
                "ayou/chat.html",
                {
                    "form": form,
                    "responsecontent": responseforuser,
                    "tokensused": tokens,
                    "name": name,
                },
            )
        else:
            return HttpResponse("FORM ERROR")
        
    """
                    if the request is GET, render the page with an empty form
    """

    name = request.user.username
    return render(request, "ayou/chat.html", {"form": NewChatForm(), "name": name,"responsecontent": f"Hi, I'm {name}. I can tell you about myself and my past" })



def social(request):
    return render(request, "ayou/social.html")


def diary(request):
    return render(request, "ayou/diary.html")


def account(request):
    return render(request, "ayou/account.html")


def memories(request):
    return render(
        request,
        "ayou/memories.html",
        {
            "memories": Memory.objects.all(),
            "chats": Chat.objects.all(),
        },
    )
    # return HttpResponse('learn')
