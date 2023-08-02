from pyfiglet import Figlet 


def globalvariables(request):
    figletlogo=Figlet(font='bulbhead')
    renderedlogo=figletlogo.renderText('Ayou')
    return {'figletlogo':renderedlogo }

def figlettext(text, font):
    figlet=Figlet(font=font)
    figlet=figlet.renderText(text)
    return figlet
    