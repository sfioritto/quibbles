from lamson.routing import route, route_like, stateless
from lamson import queue
from app.model import talking


@route("talk@(host)")
@stateless
def TALK(message, host=None):

    user = talking.get_user(message)
    conv = talking.create_conversation(user)
    snip = talking.create_snip(message, conv)
    messages = talking.get_answer_messages(snip)

    for msg in messages:
        q = queue.Queue("run/work")
        q.push(msg)

    for work in talking.get_work():
        talking.send(work, user)


@route("answer_(answer_id)@(host)",
       "mod_(mod_id)@(host)")
def START(*args, **kwargs):
    return ANSWERING(*args, **kwargs)


@route_like(START)
def ANSWERING(message, answer_id=None, snip_id=None, host=None):
    
    user = talking.get_user(message)

    if answer_id:
        answer = talking.get_answer(answer_id)
        answer.text = talking.scrape_response(message)
        answer.save()
        snip = answer.snip

        if snip.ready_to_moderate():
            modwork = talking.create_mod_email(snip)
            q = queue.Queue("run/work")
            q.push(msg)

    # we got a moderated response
    elif snip_id:
        snip = talking.get_snip(snip_id)
        talking.create_mod(snip, message)

    if user.enough_karma():
        user.use_karma()
        talking.continue_conversation(user)



