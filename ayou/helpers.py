from pyfiglet import Figlet 


def globalvariables(request):
    figletlogo=Figlet(font='bulbhead')
    renderedlogo=figletlogo.renderText('Ayou')

    heading = figlettext('Chat with your Ayou clone', 'small')
    figletsubheading = figlettext('Chat with another Ayou clone', 'small')
    return {'figletlogo':renderedlogo,'heading':heading,'figletsubheading':figletsubheading, 'pagebodyclass': 'chatbodyclass',  'pagemenuwideclass': 'chatmenuwideclass'  }

def figlettext(text, font):
    figlet=Figlet(font=font)
    figlet=figlet.renderText(text)
    return figlet

def figletheadings(request, name):
    if request.user.username != name:
        selectedagentheading = figlettext(name, 'small')        
        heading = figlettext('Chat with ', 'small')
    else:
        selectedagentheading = ''
        heading = figlettext('Chat with your Ayou clone', 'small')
    figletsubheading = figlettext('Chat with someone else', 'small')
    return  heading, selectedagentheading, figletsubheading
    
    '''
chat variables

selectagentforms()
agentslist
figletsubheading

no message to me 




global variables

name
heading


'''