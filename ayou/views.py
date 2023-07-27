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
    nickname = request.user.username

    print(f':::usernam {nickname}')
    print(">>>chatF name> ", name)
    

    def getusermemories(users_id):
        print("/// userid mfn ", userid)
        memoryquery = Memory.objects.filter(user=users_id)
        print("/// memoryquery mmfn ", memoryquery)
        memories = []
        for memory in memoryquery:
            memorydict = {
                "id": memory.id,
                "description": memory.description,
                "emotion": memory.emotion
            }
            print(f'/// Memory: {memory}')
            memories.append(memorydict)
        print("/// memorieslist  mfn ", memories)
        return memories

    def getmemorycontent(memory_id):
        memory = Memory.objects.get(id=memory_id)
        return json.dumps(memory.content)
    

    if request.method == "POST":
        form = NewChatForm(request.POST)

        if form.is_valid():
            startnewchat = form.cleaned_data["startnewchat"]
            # print(">>> startnewchat? ", startnewchat)
            # ensure there is a chat
            if not Chat.objects.all() or startnewchat:
                thischat = Chat.objects.create()
                print(">>> new thisChat> ", thischat)

                
            # print(">>> num chats  ", Chat.objects.count())
            usercontent = form.cleaned_data["usercontent"]
            thischat = Chat.objects.order_by("id").last()
            # print(">>> thischat.id ", thischat.id)
            print(
                ">>> thischat msgs>>>type ", thischat.messages, type(thischat.messages)
            )
            # create new message dict with form data
            newusermessagedict = {"role": "user", "content": usercontent}
            # print(">>> newusermessagedict ", newusermessagedict)
            # append the newusermessagedict to the stored message list
            # get the existing messages list/create it,  and append newmessage
            allmessages = thischat.messages or []
            allmessages.append(newusermessagedict)
            # print(">>> thischat.messages ", thischat.messages, type(thischat.messages))
            # print(">>> allmessages type  ", type(allmessages))
            # print(">>> allmessages ", allmessages)

            
            
            # add system message
            memorieslist = getusermemories(userid)
            systemprompt = f'You are the helpful digital representation of {name}.  Keep your answers to no more than 2 sentences. Your digital mind is still young and you have a lot to learn. But you also remember quite a lot'
            systemmessage = {"role": "system", "content": systemprompt}
            messagesforcompletion = allmessages.copy()
            messagesforcompletion.append(systemmessage)
            # print(">>> asystemmessage ", systemmessage)
            print('>>> memorieslist ', memorieslist)    

            #   >>>>>>>>>>  messagesforcompletion now has the user message and the system prompt

            # define the functions
            functions = [
                {
                    "name": "getmemorycontent",
                    "description": f"if you need information about a memory, look in this list : {memorieslist} . You can retrieve details about the memory  by calling this function with the id of the memory as the parameter. TYou will use  this new information to answer the question.",
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
            # define completion parameters
            # parameters = 'model="gpt-3.5-turbo", messages = allmessages, max_tokens = 200, temperature=1, functions=functions, function_call='auto''

            # get the openAI initial response
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagesforcompletion,
                max_tokens=200,
                temperature=1,
                functions=functions,
                function_call="auto",
            )
            print(">>> completion> ", completion)

            """
            check if this response is a functioncall!!!!
                if it is, call the function and append the result to the messagesforcompletion
            """

            # extract agent response
            responsecontent = completion.choices[0].message["content"]
            print(">>> responsecontent> ", responsecontent, type(responsecontent))

            # make a dict of all the messages
            responsedict = completion.choices[0].message
            print(">>> responsedict> ", responsedict, type(responsedict))
            print(">>> allchoices> ", completion.choices)
            # check if a memory is requested

            if responsedict.get("function_call"):
                print('>>> functioncalled')
                possfunctions = {"getmemorycontent": getmemorycontent}
                functionname = responsedict["function_call"]["name"]
                functiontocall = possfunctions[functionname]
                print('>>> functiontocall ', functiontocall)
                functionargs = json.loads(responsedict["function_call"]["arguments"])
                print('>>> functionargs ', functionargs)
                functionresponse = functiontocall(**functionargs)
                print('>>> functionresponse ', functionresponse)
                messagesforcompletion.append(
                    {
                        "role": "function",
                        "name": functionname,
                        "content": functionresponse,
                    }
                )
                print('>>>/////// messagesforcompletion ', messagesforcompletion)
                # make second agent call with function results
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messagesforcompletion,
                    max_tokens=200,
                    temperature=1,
                    functions=functions,
                    function_call="auto",
                )
                print(">>> fn completion> ", completion)
                # extract agent response
                responsecontent = completion.choices[0].message["content"]
                print(
                    ">>> fn responsecontent> ", responsecontent, type(responsecontent)
                )
                # make a dict of all the messages
                responsedict = completion.choices[0].message
                print(">>> fn responsedict> ", responsedict, type(responsedict))
            else:
                print('>>> no functioncalled')
                pass

            tokens = completion.usage.total_tokens
            print(">>> total_tokens ", tokens)
            # append the AI response and save
            allmessages.append(responsedict)
            print(">>> allmessages b4 save ", allmessages)
            thischat.messages = allmessages
            thischat.save()
            # look up a memory
            # name = request.user.username
            return render(
                request,
                "ayou/chat.html",
                {
                    "form": form,
                    "responsecontent": responsecontent,
                    "tokensused": tokens,
                    "name": name,
                },
            )
        else:
            return HttpResponse("FORM ERROR")
    name = request.user.username
    return render(request, "ayou/chat.html", {"form": NewChatForm(), "name": name})


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
