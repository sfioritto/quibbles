from lamson.routing import route, route_like, stateless
from lamson import queue
from app.model import talking


def create_work(message, conv):
    snip = talking.create_snip(message, conv)
    messages = talking.get_answer_messages(snip)

    for msg in messages:
        q = queue.Queue("run/work")
        q.push(msg)


def send_work(user):
    
    for work in talking.get_work(user):
        talking.send(work, user)


@route("talk@(host)")
@stateless
def TALK(message, host=None):

    user = talking.get_user(message)
    conv = talking.create_conversation(user)

    create_work(message, conv)
    send_work(user)

@route("answer-(answer_id)@(host)")
@route("mod-(snip_id)@(host)")
def START(*args, **kwargs):
    return ANSWERING(*args, **kwargs)


@route("answer-(answer_id)@(host)")
@route("mod-(snip_id)@(host)")
@route("conv-(conv_id)@(host)")
def ANSWERING(message, answer_id=None, snip_id=None, conv_id=None, host=None):
    
    user = talking.get_user(message)

    if answer_id:
        answer = talking.get_answer(answer_id)
        answer.text = talking.scrape_response(message.body())
        answer.save()
        snip = answer.snip
        
        user.add_karma()

        if snip.ready_to_moderate():
            modwork = talking.create_mod_email(snip)
            q = queue.Queue("run/work")
            q.push(modwork)

    # we got a moderated response
    elif snip_id:
        snip = talking.get_snip(snip_id)
        talking.create_mod(snip, message)

    #this is the continuation of a conversation
    elif conv_id:
        conv = talking.get_conversation(conv_id)
        if conv.pendingprompt:
            pass
        

    # if they have an outstanding conversation, send them
    # the response they've been waiting for if they have enough karma
    if user.enough_karma():
        talking.continue_conversation(user)



