from webapp.talking.models import User, Conversation, Snip, Answer, Moderated
from email.utils import parseaddr
from lamson import queue
from lamson.mail import MailResponse
from config import settings
from config.settings import relay
import re

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
        send_welcome_message(user)
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


def scrape_response(body):
    """
    Grab a chunk of text from the top of the message.
    Needs a string which is the body of the email
    """
    chunks = body.split(DELIMITER)
    if chunks:
        text = chunks[0]
    else:
        text = ""
    return text


def create_snip(message, conv):
    assert 'body' in dir(message), "Expecting a MailRequest"
    text = scrape_response(message.body())
    snip = Snip(prompt=text, 
                conversation=conv,
                sequence=get_snip_sequence(conv),
                complete=False)
    snip.save()
    return snip


def get_snip_sequence(conv):
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
    invalid = []
    work = []
    conversations = []
    
    while q.count() > 0:
        key, msg = q.pop()
        
        snip = get_snip_frm_msg(msg)

        if snip.complete:
            pass
        elif snip.conversation.user == user:
            invalid.append(msg)
        elif  snip.conversation in conversations:
            invalid.append(msg)
        else:
            work.append(msg)
            conversations.append(snip.conversation)

        if len(work) == 2:
            break
        
    for msg in invalid:
        q.push(msg)
    return work

def get_snip_frm_msg(msg):
    #TODO: this is pretty brittle
    answer_id = re.compile('answer-(%s)@(%s)' % (settings.router_defaults['answer_id'], settings.router_defaults['host']))
    snip_id = re.compile('mod-(%s)@(%s)' % (settings.router_defaults['snip_id'], settings.router_defaults['host']))
    
    frm = parseaddr(msg['From'])[1]

    snip = None
    # we can use the id to lookup an answer
    if answer_id.match(frm):
        id = answer_id.match(frm).groups()[0]
        answer = Answer.objects.get(pk=id)
        snip = answer.snip

    # we can use the id to lookup a moderated db record
    elif snip_id.match(frm):
        id = snip_id.match(frm).groups()[0]
        snip = Snip.objects.get(pk=id)

    return snip

def send(work, user):
    work['To'] = user.email
    relay.deliver(work, To=work['To'], From=work['From'])


def send_welcome_message(user):
    body = """Hi There!
I'm Mr. Quibbles.  Thanks for helping with this demo.  You're going to start receving a lot of e-mails.  We need your help, so please respond to as many as you can!  Thanks again!

The Quibbler (My extremely awesome nickname.)

PS - Don't reply to this e-mail."""
    
    message = MailResponse(From='"Mr. Quibbles" <no-reply@mr.quibbl.es>', Subject="Read this right now.", Body=body)

    send(message,user)

def get_answer_message(answer):
    
    message = MailResponse(From='"Mr. Quibbles" <answer-%s@mr.quibbl.es>' % answer.id, Subject="Pretend You're Mr. Quibbles", Body=build_answer_message_body(answer))

    return message
    

def build_mod_request_message_body(last_snip):

    body = DELIMITER + "\n\nMr. Quibbles has two options to respond to this converstation.  Read to the end of this e-mail and pick the best one."
    snips = [snip for snip in last_snip.conversation.snip_set.order_by('sequence').all()]
    body += build_complete_conversation(snips)
    answers = last_snip.answer_set.all()
    body += "\n\nOption 1: " + answers[0].text + "\nor\n\nOption 2: " + answers[1].text
        
    return clean(body)

def create_mod_email(snip):

    message = MailResponse(From='"Mr. Quibbles" <mod-%s@mr.quibbl.es>' % snip.id, Subject="Pretend You're Mr. Quibbles", Body=build_mod_request_message_body(snip))
    snip.complete = True
    
    return message

def build_response_message_body(last_snip):
    last_snip.complete = True
    last_snip.save()
    
    snips = [snip for snip in last_snip.conversation.snip_set.order_by('sequence').all()]
    
    body += build_complete_conversation(snips)
    
    return clean(body)

def build_complete_conversation(snips):
    """assumes snips are ordered from earliest to latest"""
    
    complete_conversation = DELIMITER + '\n\nThe conversation so far...\n'
    
    for snip in snips:
        if snip.complete:
            complete_conversation += '\nSomeone Said: ' + snip.prompt + '\n'
            complete_conversation += 'Mr. Quibbles: ' + snip.get_response()
        else:
            complete_conversation += '\nSomeone Said: ' + snip.prompt
            
    return clean(complete_conversation)

def build_answer_message_body(answer):
    
    body = DELIMITER + "\n\nRead to the end of this e-mail, hit reply, and continue this conversation.\n\n"
    
    snips = [snip for snip in answer.snip.conversation.snip_set.order_by('sequence').all()]
    
    body += build_complete_conversation(snips)
    
    return clean(body)

def get_snip(id):
    return Snip.objects.get(pk=id)


def clean(body):
    lines = body.split('\n')
    rtn_lines = []
    
    for line in lines:
        if not line.endswith('wrote:'):
            rtn_lines.append(line)
    
    new_body = '\n'.join(rtn_lines)
    
    return new_body.replace('>','')

def create_mod(snip, message):
    text = scrape_response(message.body())
    m = Moderated(text = text,
                  snip = snip)
    m.save()
    return m


def continue_conversation(user):
    user.use_karma()
    conv = user.conversation_set.filter(pendingprompt=False).all()[0]
    if conv:
        conv.pendingprompt = True
        conv.save()
        message = MailResponse(From='"Mr. Quibbles" <conv-%s@mr.quibbl.es>' % conv.id, Subject=conv.subject, Body=build_response_message_body(conv.get_last_snip()))
        message['To'] = user.email
        relay.deliver(message, To=message['To'], From=message['From'])



def get_conversation(id):
    return Conversation.objects.get(pk=id)
