import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay
from lamson import view


@stateless
@route("talk@(host)")
def TALK(message, host=None):
    # build a conversation model
    # generate two messages for gathering a response
    # dump them in a queue
    # pull three messages from the queue (that aren't from this user)
    # send them the three messages


@route("answer_(answer_id)@(host)",
       "mod_(mod_id)@(host)")
def START(*args, **kwargs):
    return ANSWERING(*args, **kwargs)


@route_like(START)
def ANSWERING(message, answer_id=None, mod_id, host=None):

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


