from lamson.routing import route, route_like, stateless
from lamson import queue
from app.model import talking


@route("talk@(host)")
@stateless
def TALK(message, host=None):

    user = talking.get_user(message)
    conv = talking.create_conversation(user)
    snip = talking.get_snip(message, conv)
    messages = talking.get_answer_messages(snip)

    for msg in messages:
        q = queue.Queue("run/work")
        q.push(msg)

    for work in talking.get_work():
        talking.send(work, user)


@route("answer_(answer_id)@(host)")
def START(*args, **kwargs):
    return ANSWERING(*args, **kwargs)


@route_like(START)
def ANSWERING(message, answer_id=None, host=None):
    
    user = talking.get_user(message)
    answer = talking.get_answer(answer_id)
    snip = answer.snip
    if snip.ready_to_moderate():
        modwork = talking.create_mod_email(snip)
        q = queue.Queue("run/work")
        q.push(msg)

    if user.enough_karma():
        user.use_karma()
        talking.continue_conversation(user)

    # if answer
    # add answer to the conversation
    # ask conversation if it's ready for moderate
    # generate moderate email
    # add to the work queue
    # if answerer has enough karma
    # send moderated reponse to question if it exists otherwise send fakey
    # 

    # if moderate
    # add moderate response to conversation
    # generate response email
    # send it out
    pass


