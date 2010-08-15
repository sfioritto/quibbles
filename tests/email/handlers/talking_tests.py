from config import testing
from nose.tools import *
from lamson.testing import *
from lamson.routing import Router
from lamson.mail import MailRequest
from lamson import queue
from conf import *
from webapp.talking.models import *
from app.model import talking


relay = relay(port=8823)
client = RouterConversation("somedude@localhost", "quibble_tests")
sender = "test@localhost"


def setup_func():
    Answer.objects.all().delete()
    q = queue.Queue(email('run/work'))
    q.clear()
    q = queue.Queue(email('run/queue'))
    q.clear()
    
    q = queue.Queue(email('run/queue'))
    q.clear()

    User.objects.all().delete()
    Conversation.objects.all().delete()
    Answer.objects.all().delete()
    Snip.objects.all().delete()
    Router.STATE_STORE.clear()

def teardown_func():
    pass

@with_setup(setup_func, teardown_func)
def test_talking():

    """
    This message should move the state into
    TALKING.
    """

    msg = MailRequest('fakepeer', sender, "talk@mr.quibbl.es", open(home("tests/data/emails/question.msg")).read())
    msg['From'] = sender
    Router.deliver(msg)
    q = queue.Queue(email('run/work'))
    assert q.count() == 2, "Queue count is actually %s" % str(q.count())
    assert delivered('Hi There!')


@with_setup(setup_func, teardown_func)
def test_get_work():

    """
    This message should move the state into
    TALKING.
    """
    # add some work to the work queue
    test_talking()
    
    msg = MailRequest('fakepeer', 'new@sender.com', "talk@mr.quibbl.es", open(home("tests/data/emails/question.msg")).read())
    msg['From'] = 'new@sender.com'
    
    Router.deliver(msg)
    q = queue.Queue(email('run/work'))
    assert q.count() == 3, "Queue count is actually %s" % str(q.count())
    assert len(Answer.objects.all()) == 4, "Oops. There are actually %s answers in the db, expected 4." % str(len(Answer.objects.all()))


@with_setup(setup_func, teardown_func)
def test_add_karma():
    test_get_work()
    
    ans_u = User.objects.filter(email='new@sender.com')[0]
    
    u = User.objects.filter(email=sender).all()[0]
    conv = Conversation.objects.filter(user=u).all()[0]
    s = Snip.objects.filter(conversation=conv).all()[0]
    answer = Answer.objects.filter(snip=s).all()[0]
    
    ans = MailRequest('fakepeer', 'new@sender.com', "answer-%s@mr.quibbl.es" % answer.id, open(home("tests/data/emails/answer.msg")).read())
    ans['From'] = 'new@sender.com'
    ans['To'] = "answer-%s@mr.quibbl.es" % answer.id
    Router.deliver(ans)
    
    ans_u = User.objects.filter(email='new@sender.com')[0]
    
    assert ans_u.karma == 1


@with_setup(setup_func, teardown_func)
def test_continue_conversation():

    """
    Start a conversation, get a response, continue the conversation.
    """

    test_talking()
    assert len(Conversation.objects.all()) == 1
    assert len(User.objects.all()) == 1
    u = User.objects.all()[0]
    c = Conversation.objects.all()[0]
    talking.continue_conversation(u)
    assert delivered('Hmmm...')
    c = Conversation.objects.all()[0]
    assert c.pendingprompt == True
    to = "conv-%s@mr.quibbl.es" % str(c.id)
    msg = MailRequest('fakepeer', sender, to, open(home("tests/data/emails/question.msg")).read())
    msg['to'] = to
    msg['from'] = sender
    #TODO: this doesn't affect state for some reason.
    Router.deliver(msg)
    assert len(Conversation.objects.all()) == 1
    assert len(User.objects.all()) == 1

