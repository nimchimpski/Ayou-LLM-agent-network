from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import requests, os, openai
import json

# from dotenv import load_dotenv
from .models import Memory, Biographyitem, Chat, Domain



class NewLoginForm(forms.Form):
    username = forms.CharField(label="username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")


class NewChatForm(forms.Form):
    startnewchat = forms.BooleanField(label="New topic?", required=False)
    usercontent = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), max_length=500, label="What do you want to say?")

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
        print(">>> loginview POST")
        form = NewLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            print(">>> username ", username)
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # domainslist
                if not Domain.objects.filter(user=request.user).exists():
                    defaultdomain = Domain(domain='general',user=request.user)
                    defaultdomain.save()
                return HttpResponseRedirect(reverse("ayou:memories"))
            else:
                return render(
                    request,
                    "ayou/index.html",
                    {"form": NewLoginForm()},
                )
        else:
            return render(
                request,
                "ayou/index.html",
                {"form": NewLoginForm(), },
            )

    form = NewLoginForm()
    if not request.user.is_authenticated:
        print(">>> loginview get request : not loged in")
        messages.add_message(request, messages.INFO, "Please log in.")
        return render(request, "ayou/index.html", {"form": NewLoginForm()})
    else:
        messages.add_message(request, messages.INFO, "logged in")
        return HttpResponseRedirect(reverse("ayou:chat"))

def register_view(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            messages.success(request, f'New account created. Now you can log-in as {username}')
            print(f'>>> in registerview : account created for {username}')
            return HttpResponseRedirect(reverse( 'ayou:login'))
        else:
            messages.add_message(request, messages.INFO, "Fill in the form correctly")
            return render(request, 'ayou/register.html', {'form': form})
        
    form = UserCreationForm()
    messages.add_message(request, messages.INFO, "Register to begin making your clone")
    return render(request, 'ayou/register.html', {'form': form, 'message': 'Please enter your details to register'})

@login_required
def logout_view(request):
    logout(request)
    message = "Logged out"
    return HttpResponseRedirect(reverse("ayou:login"))

@login_required
def chat(request):
    name = request.user.username
    userid = request.user.id
    print(f">>>  username  {name} id {userid}")
    memory_id = 0

    print(f'memory_id {memory_id}')
    print('>>> = maincode \n... = inside IF \n--- = inside ELSE \n/// = inside  FUNCTION')
    
    
    otheragentdomains = Domain.objects.all().exclude(user=userid)
    otheragentsdomainslist = []
    for domain in otheragentdomains:
        otheragentsdomainslist.append(
        {'agent': domain.user.username, 'domain': domain.domain})
    print(f'>>> otheragentdomainlist {otheragentsdomainslist}')
 
    def systemmessage(name, tokens=100):
        print('... systemmessage() called')
        systemmessage = {"role": "system", "content": f'You are the  clone of {name} complete with memories and  feelings.  .  You  remember many things but can consult other clones for more information. Introduce yourself as {name}. Remember to look at your available functions and memories, and elaborate on them when asked.  Keep your answers to no more than {tokens} tokens.'}
        return systemmessage
    
    # systemmessage = {"role": "system", "content": systemprompt}
    def exampleassistantmessage(name):
        print('... exampleassistantmessage() called')
        result ={"role": "assistant", "content": f"Hey! My names {name}. I'm actually a clone of {name}, and I remember quite a bit about my past. Not all my memories are good, but I'm happy to share them with you. I'm also happy to answer any questions you have about what I'm doing now, or about my past.I can also ask other clones for information about their memories."}
        return result

        
    def dealwithfunctionrequest():
        print('+++ dealwithfunctionrequest() called')
        possfunctions = {"getmemorycontent": getmemorycontent, "posttweet": posttweet, "askotheragent": askotheragent}
        functionname = completionmessage["function_call"]["name"]
        functiontocall = possfunctions[functionname]
        print('... functiontocall ', functiontocall)
        functionargs = json.loads(completionmessage["function_call"]["arguments"])
        print('... functionargs ', functionargs)
        functionresponse = functiontocall(**functionargs)
        print('... functionresponse ', functionresponse, type(functionresponse))
        messagechain.append(
            {
                "role": "function",
                "name": functionname,
                "content": functionresponse,
            }
        )
        return messagechain
    
    def askotheragent(agentname, question):
        print(f'+++ askotheragent() called {agentname} {question}')
        otheragentid= User.objects.get(username=agentname).id
        # print(f'/// otheragentid {otheragentid}')
        memorieslist = getmemorieslist(otheragentid)
        otheragentsfunctions = scopedfunctions(memorieslist)
        print(f'/// otheragentsfunctions {otheragentsfunctions}')
        print(f'/// other agents memorieslist {memorieslist}')
        messagechain = []
        messagechain.append(systemmessage(agentname))
        messagechain.append(exampleassistantmessage(agentname))
        messagechain.append({"role": "system", "content": "IMPORTANT! Make sure you have the correct id for the memory you want to retrieve"})
        # print(f'/// new messagechain {messagechain}')
        def askagent(callfunction='auto'):
            print('+++ askagent() called')
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagechain,
                max_tokens=1000,
                temperature=1,
                functions=otheragentsfunctions,
                function_call="auto",
            )
            print(f'/// askagent() completion = {completion}')
            return completion
        
        askotheragentresponse  = askagent()
                    # otheragent probably requests a memory 
                    # check memory id is valid
        mess = askotheragentresponse['choices'][0]['message']['function_call']['arguments']
        memoryiddict = json.loads(mess)
        memoryid = memoryiddict.get('memory_id')
        while not Memory.objects.filter(id=memoryid):
            print('... memory id not valid')
            askagent()
            print(f'/// memoryid {memoryid}')
            askotheragentresponse  = askagent()
            mess = askotheragentresponse['choices'][0]['message']['function_call']['arguments']
            memoryiddict = json.loads(mess)
            memoryid = memoryiddict.get('memory_id')
            attempts += 1
            if attempts >= 5:
                print(f"Failed to generate a valid memory id after 5 attempts.")
                return 'Sorry, the clone network is is down for maintainance.'

                    # we got an id/memory match,  now get memory content
        
        if not askotheragentresponse['choices'][0]['message'].get('function_call'):
            print('... no function call')
            return askotheragentresponse.choices[0].message.get('content')
        else:
            print('... function call')
            newmessage = f"Here is some information from someone you know :  {getmemorycontent(memoryid)}"
            print(f'/// askagent() newcmessage with new memory {newmessage}')
                    # t new message with the memory content
            print('...we got the otheragents info, now we need to send it back to the original agent')
            return newmessage


    def getmemorieslist(users_id):
        print(f'+++ getmemorieslist called for user {users_id}')
        memoryquery = Memory.objects.filter(user=users_id)
        # print("/// memoryquery mmfn ", memoryquery)
        memories = []
        for memory in memoryquery:
            memorydict = {
                "memory_id": memory.id,
                "description": memory.description,
                "emotion": memory.emotion
            }
            # print(f'/// Memory: {memory}')
            memories.append(memorydict)
        # print("/// memorieslist  mfn ", memories)
        return memories
    

        pass

    def getmemorycontent(memory_id):
        print(f'+++ getmemorycontent called. id= {memory_id}')
        memory = Memory.objects.get(id=memory_id)
        print(f'/// memory to be retrieved= {memory}')
        return json.dumps(memory.content)
    
    def posttweet(tweet):
        """
        DO THIS!!!
        """
        return 'pretending tweet got sent'
        
    


    memorieslist = getmemorieslist(userid)
    print('>>> memorieslist ', memorieslist)
        
    if request.method == "POST":
        form = NewChatForm(request.POST)

        if form.is_valid():
            startnewchat = form.cleaned_data["startnewchat"]
            # print(">>> startnewchat? ", startnewchat)
            # ensure there is a chat
            

            if not Chat.objects.filter(user=userid).exists() or startnewchat:
                thischat = Chat.objects.create()
                thischat.user = request.user
                print("... NEW thisChat > ", thischat)
                messagechain = []
                messagechain.append(systemmessage(name))
                messagechain.append(exampleassistantmessage(name))
                # print("... messagechain ", messagechain, type(messagechain))
            else:
                print('--- there is a chat')
                thischat = Chat.objects.filter(user=request.user).order_by("id").last()
                # print("--- thischat/type ", thischat, type(thischat))
                messagechain = thischat.messages
                # print("--- messagechain/type ", messagechain, type(messagechain))
            usercontent = form.cleaned_data["usercontent"]
            # print(">>> usercontent ", usercontent)
            newusermessagedict = {"role": "user", "content": usercontent}            
            messagechain.append(newusermessagedict)
            # print(">>> messagechain at start   ", messagechain)

            """
                    now we have a messagechain with the user's message at the end

            """      
            '''

                    functions

            '''
            def scopedfunctions(memorieslist):
                print('+++ scopedfunctions called')
                result = [
                {
                    "name": "getmemorycontent",
                    "description": f"If you need information look in this list of your personal memories, which shows thier memory_id numbers: {memorieslist} . You can retrieve details about the memory  by calling this function. You will use  this new information to answer the question. Make sure you have the correct memory_id number ",
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
                {"name": "askotheragent", "description": f"if the conversation makes you feel like you need to ask another agent a question, you can do that by calling this function. cHere is a list of other agents and their domains of knowledge:{otheragentsdomainslist}. If one of them has information you need,  give the name of the agent  and the question you want to ask them as parameter.  ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "the question you want to ask",
                            }, "agentname": {"type": "string", "description": "the name of the agent you want to ask"},
                        },
                       "required": [ "agentname", "question"]  
                    },
                },
             
            ]
                return result
            '''
            functions = [
                {
                    "name": "getmemorycontent",
                    "description": f"If you need information look in this list of your personal memories, which shows thier memory_id numbers: {memorieslist} . You can retrieve details about the memory  by calling this function. You will use  this new information to answer the question. Make sure you have the correct memory_id number ",
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
                {"name": "askotheragent", "description": f"if the conversation makes you feel like you need to ask another agent a question, you can do that by calling this function. cHere is a list of other agents and their domains of knowledge:{otheragentsdomainslist}. If one of them has information you need,  give the name of the agent  and the question you want to ask them as parameter.  ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "the question you want to ask",
                            }, "agentname": {"type": "string", "description": "the name of the agent you want to ask"},
                        },
                       "required": [ "agentname", "question"]  
                    },
                },
             
            ]
            '''         
            functions = scopedfunctions(memorieslist)
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
    
            completionmessage = firstcompletion["choices"][0]["message"]
            print(">>> completionmessage  type= ", type(completionmessage) )
            # print(">>> completionmessage  ",completionmessage, )

            """
                        
                            if functioncall in response , call it and append result to messagesforcompletion
            '"""
        
            if completionmessage.get("function_call"):
                messagechain = dealwithfunctionrequest()
                """

                           make second agent call with function results
                
                """
                completionwithfunctionresults = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messagechain,
                    max_tokens=200,
                    temperature=1,
                    functions=functions,
                    function_call="none",
                )
                # print("... 2nd completion> ", completionwithfunctionresults, type(completionwithfunctionresults))

                            #  extract agent response from secondcompletion
                responseforuser = completionwithfunctionresults.choices[0].message["content"]
                # print("... fn responseforuser> ", responseforuser, type(responseforuser))

                            #  make a dict of all the messages
                secondresponsedict = completionwithfunctionresults.choices[0]['message']
                # print(f'... fn responsedict type= {type(secondresponsedict)} ++++ {secondresponsedict}')
                tokens = completionwithfunctionresults.usage.total_tokens
                print("...> total_tokens ", tokens)
                messagechain.append(secondresponsedict)

            else:
                '''
                           if no functioncall in response 
                '''
                print('---: no functioncalled')
                            #  this goes to the htnl page later
                responseforuser = firstcompletion.choices[0].message["content"]
       

                            #   this will be added to the chain
                firstresponsedict = {'role': 'assistant', 'content': f'{firstcompletion.choices[0].message["content"]}'}    
                
                tokens = firstcompletion.usage.total_tokens
                print("--- total_tokens ", tokens)
                messagechain.append(firstresponsedict)
                # print("--- messagechain b4 save ", messagechain)
          
            print('>>> messagechain b4 IF summary ', messagechain)

            """
                            before saving, is the chain too long?
            """

            if tokens >1800:
                print('...inside summary block')
                summariserequestmessage = {"role": "system", "content": "IMPORTANT! summarise the  conversation so far, using no more than 300 tokens. "}
                messagechain = messagechain[2:]
                messagechain.append(summariserequestmessage)
                # print('... toolong messagechain ', messagechain)

                """
                            completion to summarise the chain 
                            loose the first 2 dicts in the chain!

                """
                summarycompletion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messagechain,
                temperature=0.3
                )
                # print('... summarycompletion ', summarycompletion)
                summarisedtokencount = summarycompletion.usage.total_tokens
                print('... summarisedtokencount ', summarisedtokencount)

                summarycompletioncontent = summarycompletion.choices[0].message
                # print('... summarycompletioncontent ', summarycompletioncontent)
                # summarycompletionmessage = {"role": "assistant", "content": f"PREVIOUS CHAT SUMMARY: {summarycompletioncontent}"}
                messagechain = []
                messagechain.append(systemmessage(name, 100))
                messagechain.append(exampleassistantmessage(name))
                messagechain.append(summarycompletionmessage)
                print('...> sumarised messagechain ', messagechain)
            #       append the agent response and save the chat
            # print('>>> messagechain after summaryblock ', messagechain)
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
        print(f'... domainslist  {domainslist} type {type(domainslist[0])}')
        
        
    

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
    messages.add_message(request, messages.INFO, f"logged in as {request.user.username}")
    return render(request, "ayou/memories.html", pagevariables(request, message))
    # return HttpResponse('learn')
