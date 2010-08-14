from webapp.talking.models import User, Conversation, Snip, Answer, Moderated
from email.utils import parseaddr
from lamson import queue
from lamson.mail import MailResponse
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


def scrape_response(message):
    """
    Grab a chunk of text from the top of the message.
    """
    chunks = message.body().split(DELIMITER)
    if chunks:
        text = chunks[0]
    else:
        text = ""
    return text


def create_snip(message, conv):
    text = scrape_response(message)
    snip = Snip(prompt=text, 
                conversation=conv,
                sequence=_get_snip_sequence(conv))
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


def get_answer(id):
    
    return Answer.objects.get(pk=id)


def get_work(user):
    
    q = queue.Queue("run/work")
    work = []
    invalid = []

    # this may return an empty list of work
    while q.count > 0:
        u, msg = q.pop()
        if user == u:
            invalid.append((u, msg))
        else:
            work.append(msg)
            if len(work) == 3:
                break

    for i in invalid:
        q.push(i)

    return work


def send(work, user):
    work['To'] = user.email
    relay.deliver(work, To=work['To'], From=work['From'])


def get_answer_message(answer):
    
    message = MailResponse(From="answer-%s@mr.quibbl.es" % answer.id, Subject="Mr. Quibbles wants to your input", Body=build_answer_message_body(answer))

    return message

def create_mod_email(snip):

    message = MailResponse(From="mod-%s@mr.quibbl.es" % snip.id, Subject="Mr. Quibbles wants you to know...", Body=build_mod_message_body(snip))
    
    return message

def build_mod_message_body(last_snip):
    
    snips = [snip for snip in last_snip.conversation.snip_set.order_by('sequence').all()]
    
    body = 'The conversation so far...\n'
    for snip in snips:
        body += DELIMITER + '\n\nYou: ' + snip.prompt + '\n\n'
        body += DELIMITER + '\n\nMr. Quibbles: ' + snip.get_response() + '\n\n'
    
    return body

def build_answer_message_body(answer):
    
    snips = [snip for snip in answer.snip.conversation.snip_set.order_by('sequence').all()][:-1]
    
    body = 'The conversation so far...\n'
    for snip in snips:
        body += DELIMITER + '\n\nYou: ' + snip.prompt + '\n\n'
        body += DELIMITER + '\n\nMr. Quibbles: ' + snip.get_response() + '\n\n'
    body += DELIMITER + '\n\nYou: ' + answer.snip.prompt + '\n\n'
    return body


def get_snip(id):
    return Snip.objects.get(pk=id)


def create_mod(snip, message):
    text = scrape_response(message)
    m = Moderated(text = text,
                  snip = snip)
    m.save()
    return m


def continue_conversation(user):
    pass
