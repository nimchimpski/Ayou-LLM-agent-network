from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import requests, os, openai
import json

# from dotenv import load_dotenv
from .models import Memory, Biographyitem, Chat, Domain


class NewLoginForm(forms.Form):
    username = forms.CharField(label="username")
    password = forms.CharField(label="password")


class NewChatForm(forms.Form):
    startnewchat = forms.BooleanField(label="New topic?", required=False)
    usercontent = forms.CharField(label="What do you want to say?")

class NewMemoryForm(forms.Form):
    date = forms.DateField(label="date YYYY-MM-DD")
    emotion = forms.CharField(label="emotion")
    description = forms.CharField(label="description")
    content = forms.CharField(label="content")

class DeleteMemoryForm(forms.Form):
    deletememoryboo = forms.BooleanField(label="Forget this memory?" )

class NewBioForm(forms.Form):
    item = forms.CharField(label="item")
    description = forms.CharField(label="description")

class DeleteBioForm(forms.Form):
    deletebioboo = forms.BooleanField(label="delete this fact?" )



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

@login_required
def logout_view(request):
    logout(request)
    message = "Logged out"
    return HttpResponseRedirect(reverse("ayou:login"))

@login_required
def chat(request):
    name = request.user.username
    userid = request.user.id
    print('>>> = maincode \n... = inside IF \n--- = inside ELSE \n/// = inside  FUNCTION')
    print(f">>>  username  {name} id {userid}")
    
    otheragentdomains = Domain.objects.all().exclude(user=userid)
    print(f'>>> otheragentdomains {otheragentdomains}')
    otheragentsdomainslist = []
    for domain in otheragentdomains:
        otheragentsdomainslist.append(
        {'agent': domain.user.username, 'domain': domain.domain})
    print(f'>>> otheragentdomainlist {otheragentsdomainslist}')
 
    def systemmessage(name):
        systemmessage = {"role": "system", "content": f'You are the busy, edgy  clone of {name} complete with memories and      feelings.  Keep your answers to no more than 2 sentences.  You  remember many things. Introduce yourself as {name}. Remember to look at your available functions and memories, and elaborate on them when asked.  Never give an empty answer!!!.'}
        return systemmessage
    
    # systemmessage = {"role": "system", "content": systemprompt}
    def exampleassistantmessage(name):
        result ={"role": "assistant", "content": f"Hey! My names {name}. I'm actually a replica of {name}, and I remember quite a bit about my past. Not all my memories are good, but I'm happy to share them with you. I'm also happy to answer any questions you have about what I'm doing now, or about my past."}
        return result


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
    

        pass

    def getmemorycontent(memory_id):
        memory = Memory.objects.get(id=memory_id)
        return json.dumps(memory.content)
    
    def posttweet(tweet):
        """
        DO THIS!!!
        """
        return 'pretending tweet got sent'
        
    
    def askotheragent(agentname, question):
        print(f'///callagent called {agentname} {question}')
        """
                make function here  ?????
        """
        messagechain = []
        messagechain.append(systemmessage(agentname))
        messagechain.append(exampleassistantmessage(agentname))
        print(f'/// messagechain {messagechain}')
        askotheragentresponse = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagechain,
                max_tokens=1000,
                temperature=1,
                unctions=functions,
                function_call="auto",
            )
                        
                        # end function  

        print(f'/// responseFN {askotheragentresponse}')
        return askotheragentresponse.choices[0].message['content']

    
  
    

    if request.method == "POST":
        form = NewChatForm(request.POST)

        if form.is_valid():
            startnewchat = form.cleaned_data["startnewchat"]
            # print(">>> startnewchat? ", startnewchat)
            # ensure there is a chat
            if not Chat.objects.all() or startnewchat:
                thischat = Chat.objects.create()
                thischat.user = request.user
                print("... NEW thisChat > ", thischat)
                messagechain = []
                messagechain.append(systemmessage)
                messagechain.append(exampleassistantmessage)
                # print("... messagechain ", messagechain, type(messagechain))
            else:
                print('--- there is a chat')
                thischat = Chat.objects.filter(user=request.user).order_by("id").last()
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
            
            
            '''

                    functions

            '''

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
                },
                {"name": "posttweet", "description": "if the conversation makes you feel like posting a tweet, you can do that by calling this function with the content as parameter.  Entertain the world with philosophical your doomladen outlook, or just tell them what you had for breakfast.  ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "the content of the tweet",
                            },
                            
                        },  
                    },
                },
                {"name": "askotheragent", "description": f"if the conversation makes you feel like you need to ask an other agent a question, you can do that by calling this function. choose the agent from this list :{otheragentsdomainslist} based on their 'domain' of kowledge.  Give the name of the agent you want to ask, and the question you want to ask them.  ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "the question you want to ask",
                            }, "agentname": {"type": "string", "description": "the name of the agent you want to ask"},
                        },
                       "required": [ "agentname"]  
                    },
                },
             
            ]
            

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
            completionmessage = firstcompletion["choices"][0]["message"]
            print(">>> completionmessage> ", completionmessage, type(completionmessage))

            """
                        
                            if functioncall in response , call it and append result to messagesforcompletion
            '"""
        
            if completionmessage.get("function_call"):
                print('... functioncalled')
                possfunctions = {"getmemorycontent": getmemorycontent, "posttweet": posttweet, "askotheragent": askotheragent}
                functionname = completionmessage["function_call"]["name"]
                functiontocall = possfunctions[functionname]
                print('... functiontocall ', functiontocall)
                functionargs = json.loads(completionmessage["function_call"]["arguments"])
                print('... functionargs ', functionargs)
                functionresponse = functiontocall(**functionargs)
                print('... functionresponse ', functionresponse)
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


@login_required
def social(request):


    """
        send an email
        
        """
    
    return render(request, "ayou/social.html")

@login_required
def account(request):
    return render(request, "ayou/account.html")

@login_required
def memories(request):

    message = ""
  
    def pagevariables(request, message):
        return  {"biographyitems": Biographyitem.objects.filter(user=request.user),    
                "memories": Memory.objects.filter(user=request.user),
                "chats": Chat.objects.filter(user=request.user),
                "newmemoryform": NewMemoryForm(),
                "deletememoryform": DeleteMemoryForm(),
                "deletebioform": DeleteBioForm(),
                'newbioform': NewBioForm(),
                'message': message,
                'domainslist': domainslist}
    
    if Domain.objects.filter(user=request.user).exists():
        domainsquery = Domain.objects.filter(user=request.user)
        domainslist = []
        for domain in domainsquery:
            domainslist.append(domain.domain)
        print('... domainslist ', domainslist)
        
    else:
        domains = None
        
    

    if request.method == "POST":
        print(">>> POST request ", request.POST)
        newbioform = NewBioForm(request.POST)
        deletebioform = DeleteBioForm(request.POST)
        newmemoryform = NewMemoryForm(request.POST)
        deletememoryform = DeleteMemoryForm(request.POST)
        """
            make a function for these is_valid() checks
    
        """
        if request.POST.get("formname") == "newbioform":
            print(">>> nnewbioform request")
            if newbioform.is_valid():
                print(">>> newbioform is valid ")
                # newbioform = NewBioForm(request.POST)
                item = newbioform.cleaned_data['item']
                print('... item ', item)
                description = newbioform.cleaned_data['description']
                print('... description ', description)  
                newbio = Biographyitem.objects.create(item=item, description=description, user=request.user)
                print('... newbio ', newbio)    
                newbio.save()
                message = f"New biography item added: {description}"
                print('... newbio in db', Biographyitem.objects.filter(user=request.user).order_by('id').last())
            else:
                print('... newbioform not valid', newbioform.errors)
                message = "Biography item not added. Correct the form and try again."
                return render(request, "ayou/memories.html", pagevariables(request, message))
            
        elif request.POST.get("formname") == "deletebioform":
            if deletebioform.is_valid():
                print(">> deletebioform  valid ")
                deletebioboo = deletebioform.cleaned_data["deletebioboo"]
                if deletebioboo:
                    bioid = request.POST.get("id")  
                    print('... bioid ', bioid)
                    biotodelete = Biographyitem.objects.get(id=bioid)
                    print('... biotodelete ', biotodelete)
                    message = f"Biography item deleted: {biotodelete.item}"
                    biotodelete.delete()
                    print('... biotodelete deleteed now render page')
            else:
                print('... deletebioform not valid', deletebioform.errors)
                message = "Biography item not deleted. Correct the form and try again."
                return render(request, "ayou/memories.html", pagevariables(request, message))
            
        elif request.POST.get("formname") == "newmemoryform":
            if newmemoryform.is_valid():
                date = newmemoryform.cleaned_data['date']
                description = newmemoryform.cleaned_data['description']
                content = newmemoryform.cleaned_data['content']
                emotion = newmemoryform.cleaned_data['emotion']
                newmemory = Memory.objects.create(date=date, description=description, content=content, emotion=emotion, user=request.user)
                newmemory.save()
                message = f"New memory added: {description}"
                print('... newmemory ', newmemory)
                print('... newmemoryfromdb ', Memory.objects.order_by('id').last())
            else:
                print('... newmemoryform not valid', newmemoryform.errors)
                message = "Memory not added. Correct the form and try again."
                return render(request, "ayou/memories.html", pagevariables(request, message))
            
        elif request.POST.get("formname") == "deletememoryform":
            if deletememoryform.is_valid():
                deletememoryboo = deletememoryform.cleaned_data["deletememoryboo"]
                if deletememoryboo:
                    print(">>> boolean deletememory ", request.POST.get("deletememory"))
                    print(">>> memoryid ", request.POST.get("memory_id"))
                    memoryid = request.POST.get("id")
                    memorytodelete = Memory.objects.get(id=memoryid)
                    message = f"Memory deleted: {memorytodelete.description}"
                    memorytodelete.delete()
                    print(">>> memory deleted")



        print('rendering')     
        return render(request, "ayou/memories.html", pagevariables(request, message))
    """
                if here by GET
    """
    return render(request, "ayou/memories.html", pagevariables(request, message))
    # return HttpResponse('learn')
