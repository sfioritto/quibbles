from webapp.talking.models import User, Conversation
from email.utils import parseaddr

DELIMITER = '------------------------------'

def get_from_address(message):
    name, address = parseaddr(message['from'])
    
    
def get_user(message):
        
    addr = get_from_address(message)
    user = find_user(addr)

    if not user:
        user = User(email = addr)
        user.save()
    return user


def find_user(address):
    users = User.objects.filter(email = address)
    if users:
        return users[0]
    else:
        return None


def create_conversation(user):

    conv = Conversation(user=user)
    conv.save()
    return conv


def get_snip(message, conv):

    chunks = message.body().split(DELIMITER)
    if chunks:
        text = chunks[0]
    else:
        text = ""


    snip = Snip(prompt=text, 
                conversation=conv)
    snip.save()


def get_answer_messages(snip):
    
    a1 = Answer(snip=snip)
    a2 = Answer(snip=snip)
    a1.save()
    a2.save()

    
                 

    
    
    


    
