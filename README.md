# 'AYOU' (Artificial You)

#### VIDEO DEMO:  [http://nimchimpski.com/ayou.mp4](http://nimchimpski.com/ayou.mp4)
Note on the video. Because it would not be clear if an agent was actually contacting another, or just accessing the LLM training data, I decided to make somewhat ridiculous agent examples, such that when they returned memory information to a calling agent, it was clear it had to have come from them. 
Eg. (as far as I know) there is no Fat Constants Theory!


## DESCRIPTION / AIM:
A web application where users can create of a personalised, configurable chatbot, 
which can recall the history of a conversation. Note: the OpenAI completions API has no initial memory function.
The agent can be configured with biographical details and memories. These can be retrieved as and when deemed necessary by the agent.
It can ask other agents to share information stored in their memories. Likewise, if asked, it can share its own memories
The user can select other users' agents to chat to.

-----

## USER INTERFACE -  (FRONT-END) EXPERIENCE
Each user has their own agent, who they are confronted with once logged in.
The page collapses to a small width with one breakpoint.
There are 3 menu buttons at the top; Chat, Configure and Logout.
Messages per the loggin-status appear top right.

### index.html (login)
A simple username/password login, using Django authentication.
The login page background-image is animated to slowly pan from side to side.
Option to have forgotten passwords emailed (if an email adress has been added by Admin), or to  go to...

### registration.html
Django built in registration form, with name and complexity checked password.
User is initially redirected to...

### memories.html (configure page) 
 
There are 3 categories of data which can be inputed here.
If already uploaded, these are presented as lists.

1 a 'knowledge area'. This is one record per agent, which can contain a string describing what knowledge (stored as memories) the agent has.
This is shared with all agents. 
This can be edited.

2 'biographical fact's'. arbitrary number of items describing the person, such as adress, age, hair colour, personality.
Option to delete items.
This is personal.

3 'memories'. arbitrary number of items, each with a date, short description, main content, and an emotion.
These are personal, but can be recalled if wanted , and shared with other agents if requested.
Option to delete items

Password can be reset on this page.

Clicking the menu Chat button leads to...

### chat.html 
here the agent can be talked to by inputing text, following on from a previous conversation which is automatically retrieved.
If preferred a 'new chat' option can be selected.
The agent response appears above the user input field.
It slowsly and subtly pulsates with a reversing orange/blue gradient

Below, there is a list of all the other agents that have been created. 
These can be selected to chat with. Naturally, the initial loggen in user remains the same.
The name of the agent, if not ones own, is displayed in Figlet font.

------


#### PROJECT CODE USED
python, html, css
#### FRAMEWORKS USED
Django

## CODE/FRONTEND

There is a main 'layout'html' template carrying the menu.

The HTML'CSS is all vanilla. No framework for this beyond whats included in Django.
Css body classes are passed to individual  html template pages to control the background image which is used for the menu as well, thus creating a 'transparent' menu bar effect, under which content, as normal,  scrolls invisibly.

As mentioned, there are 2 animations.
Login page sci-fi city background-image pans slowly.
Agent response box 'pulsates' by animating a color-gradient reversal.

Figlet 'Bulbhead' font is used for the main Ayou logo.
Unfortunately at smaller sizes, and for the text I needed, it was not sufficiently legible, so for the other headings I used Figlet 'small'.




## CODE/BACKEND

all the main code is in views.py,

### REGISTRATIOM / LOGIN VIEW
This is done  using Django's built in registration and authentication system. Passwords must meet a criteria of complexity and are stored as hashes.

On creation a couple of things happen.
A knowledge area record is created, with the  field set to a default 'general'.
The user.object has a field called 'selectedagent' set to the user.
(this is crucial to how parts of the program will know which agent it is dealing with)


### CHAT VIEW
On receiving a POST request (in this case carrying user chat input and optional new-chat selection);
From the database:
A list of the other agents
A list of the  personal biographical items
A list of the agents memories
A list of the other agents domains of knowledge
are all retrieved.

If the option to select another agent was taken, the identity of that agent is stored in the user object, and the global name variable is changed to equal that.

If it is standard chat request, and there is not already a chat in the database for this user, or a new one is requested, it is now created. This is initialised with a system message and example agent response.These contain a list of the agents biographical details, a list of the memories, 
If there is an existing chat, it is retrieved, and the user question/content is appended to the 'chain', along with a short sytem message reminding the agent to act in character. [This was a late addition and seemed to improve the responses.]

The agent is supplied with the description of 2 functions. This is not appended to the chain.
1 - from its list of memories it can decide to retrieve a specific one, each being identified by an ID number.
2 - it can decide to 'ask another agent'
It can request for either of these to be called.

The initial call to the OpenaI API is made with the chat chain and the function list.

The response is checked for any function requests.
If necessary, a memory content is retrieved and sent directly back to the agent (nothing yet goes to the webpage) for processing.
Or if required another agent is contacted.
This is done inside a function which switches the current agent name accordingly, such that bio items and memory list all now pertain to the second agent. Of course it now needs to request one of its own memories,
before it can send the information back to the oringinal agent, who in turn can ultimately answer the initiating question from the user.

I limited the attempts allowed for the called agent to respond with a meaingful memory request, to avoid non-ending loops.

I would like to implement this recursively, but with just one level of requests I think there would be no benefit.

Finally the memory content from the called agent is appended to the (original) message chain, with a system message explaining how to use it.
Another API call is made, with the agent identity now set back as the original 'selectedagent'. The relevant response content from this is passed to the html page for the user.

If the chat exceeds a specified length, it is sent to the agent to be summarised, and the result is saved in place of the original chain.
The API charges by Token use, so the length is important. Also once it gets too long , writing it to memory every conversational turn has too high a time cost. This is also a chance to put the full system message back into focus to the agent, by appending to the  start of the new chain.

### MEMORIES VIEW (CONFIGURE)

The database has 3 models accessable through the forms on this page.
Domain (knowledge area), BiographicalItem, and Memory.
These are basic form fields, each a with a hidden identifier field so that it can be filtered in the view POST processing.
Bio items and memories can be deleted, but not edited.
A message confirms creation or deletion of entries.

Forms are all created with Django form classes, using widgets to specify css-classes

-----

## other files

#### Helpers.py
a globalvariables function, for the Figlet font headings

#### styls.css
Basic css file.
Used flex where possible
One media query breakpoint to collapse the menu and reposition the background picture.

#### index.html, memories.html, chat.html, register.html, layout.html,
simple html.pages, as described above.

#### models.py
the sqlite3 database tables. (Chat, Memory, BiographyItem, Domain)


# DESIGN CHOICES

design decisions - no javascript, no css framework just plain css.
Keep a minimum of pages.
**IMPORTANT** OpenAI chat completions API has no memory, (ala chatGPT) so the first goal was to implement chat history storage and retrieval.

## original ideas, not implemented due to time constraints

A 'Social' page, where the agent could be configured to , eg, via Twitter API, read certain tweets and post. Respond to certain emails, and reply to specific Whatsapp messages.
A message with eg. "Thinking" displayed instead of the previous agent response once the user submits a question. This could be via AJAX/fetch.
Seperation of chats not carried out with the owner of that agent.
Old chat retieval. 
User Email input.
