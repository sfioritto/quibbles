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
                sequence=get_snip_sequence(conv))
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

    while q.count() > 0:
        key, msg = q.pop()

        if find_owner(msg) == user:
            invalid.append(msg)
        else:
            work.append(msg)

        if len(work) == 3:
            break
        
    for msg in invalid:
        q.push(msg)
    return work


def find_owner(msg):

    #TODO: this is pretty brittle
    answer_id = re.compile('answer-(%s)@(%s)' % (settings.router_defaults['answer_id'], settings.router_defaults['host']))
    snip_id = re.compile('answer-(%s)@(%s)' % (settings.router_defaults['snip_id'], settings.router_defaults['host']))
    
    frm = msg['From']

    user = None
    # we can use the id to lookup an answer
    if answer_id.match(frm):
        id = answer_id.match(frm).groups()[0]
        answer = Answer.objects.get(pk=id)
        user = answer.snip.conversation.user

    # we can use the id to lookup a moderated db record
    elif snip_id.match(frm):
        id = snip_id.match(frm).groups()[0]
        mod = Moderated.objects.get(pk=id)
        user = mod.snip.conversation.user

    return user



def send(work, user):
    work['To'] = user.email
    relay.deliver(work, To=work['To'], From=work['From'])


def get_answer_message(answer):
    
    message = MailResponse(From="answer-%s@mr.quibbl.es" % answer.id, Subject="Mr. Quibbles wants your input", Body=build_answer_message_body(answer))

    return message

def create_mod_request_email(snip):
    message = MailResponse(From="mod-%s@mr.quibbl.es" % snip.id, Subject="Mr. Quibbles wants you your input...", Body=build_mod_request_message_body(snip))
    

def build_mod_request_message_body(last_snip):

    body = DELIMITER + """
        Mr. Quibbles: I heard this through the grapevine -
            
            \"""" + last_snip.prompt + """\"
            
        Copy and paste the best response, or write your own.
        
        """
    answers = last_snip.answer_set.all()
    
    body += """    """ + answers[0].text + """
                
                or
                
            """ + answers[1].text + '\n\n'
    
    moderated_snips = [snip for snip in last_snip.conversation.snip_set.order_by('sequence').all()][:-1]
    body += build_unmoderated_message_previous_conversation(last_snip, moderated_snips)
    
    return body

def create_mod_email(snip):

    message = MailResponse(From="mod-%s@mr.quibbl.es" % snip.id, Subject="Mr. Quibbles wants you your input...", Body=build_mod_message_body(snip))
    
    return message


def build_mod_message_body(last_snip):
    
    snips = [snip for snip in last_snip.conversation.snip_set.order_by('sequence').all()]
    
    body = DELIMITER + '\n\nMr. Quibbles: ' + snips[-1].get_response() + '\n\n'
    body += build_moderated_message_previous_conversation(snips)
    
    return body


def build_moderated_message_previous_conversation(snips):
    previous_conversation = DELIMITER + '\n\nThe conversation so far...\n'
    
    for snip in snips:
        previous_conversation += DELIMITER + '\n\nYou: ' + snip.prompt + '\n\n'
        previous_conversation += DELIMITER + '\n\nMr. Quibbles: ' + snip.get_response() + '\n\n'
    
    return previous_conversation


def build_unmoderated_message_previous_conversation(unmoderated_snip, moderated_snips):
    previous_conversation = DELIMITER + '\n\nThe conversation so far...\n'
    
    for snip in moderated_snips:
        previous_conversation += DELIMITER + '\n\nYou: ' + snip.prompt + '\n\n'
        previous_conversation += DELIMITER + '\n\nMr. Quibbles: ' + snip.get_response() + '\n\n'
    previous_conversation += DELIMITER + '\n\nYou: ' + unmoderated_snip.prompt + '\n\n'
    
    return previous_conversation

def build_answer_message_body(answer):
    
    snips = [snip for snip in answer.snip.conversation.snip_set.order_by('sequence').all()][:-1]
    
    body = build_unmoderated_message_previous_conversation(answer.snip,snips)
    
    return body

def get_snip(id):
    return Snip.objects.get(pk=id)


def create_mod(snip, message):
    text = scrape_response(message.body())
    m = Moderated(text = text,
                  snip = snip)
    m.save()
    return m


def continue_conversation(user, conv):
    user.use_karma()
    conv.pendingprompt = True
    conv.save()
    message = MailResponse(From="conv-%s@mr.quibbl.es" % conv.id, Subject=conv.subject, Body=build_conversation_body(answer))
    message['To'] = user.email
    relay.deliver(message, To=message['To'], From=message['From'])



def get_conversation(id):
    return Conversation.objects.get(pk=id)
