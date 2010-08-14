from webapp.talking.models import User, Conversation
from email.utils import parseaddr
from lamson import queue
from lamson.mail import MailRequest
from config.settings import relay


DELIMITER = '------------------------------'

def get_from_address(message):
    name, address = parseaddr(message['from'])
    return address
    
    
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
                conversation=conv,
                sequence=_get_snip_sequence())
    snip.save()
    return snip

def _get_snip_sequence(conv):
    last_snip = conv.get_last_snip()
    
    if last_snip == None:
        return 0
    else:
        return last_snip.sequence + 1

def get_answer_messages(snip):
    
    a1 = Answer(snip=snip)
    a2 = Answer(snip=snip)
    a1.save()
    a2.save()
    
    return get_answer_message(a1), get_answer_message(a2)


def get_work():
    
    q = queue.Queue("run/work")
    return [q.pop()[1], q.pop()[1]]


def send(work, user):
    work['To'] = user.email
    relay.deliver(work, To=work['To'], From=work['From'])


def get_answer_message(answer):
    
    message = MailResponse(From="mr.quibbles-%s@quibbl.es" % answer.id, Subject="Mr. Quibbles wants to know...", Body=build_message_body(answer))

    return message

def build_answer_message_body(answer):
    
    snips = answer.snip.conversation.snip_set.all()
    snips.order_by('-sequence')
    
    message = answer.snip.prompt + ('\n'*2)
    
    for index in range(len(snips),1):
        snip = snips[index]
        message += DELIMITER + ('\n'*2) + snip.get_response() + ('\n'*2)
        message += DELIMITER + ('\n'*2) + snip.prompt + ('\n'*2)
    
    return message
