from config import testing
from nose.tools import *
from lamson.testing import *
from lamson.routing import Router
from lamson.mail import MailRequest
from lamson import queue
from conf import *
from webapp.talking.models import Answer


relay = relay(port=8823)
client = RouterConversation("somedude@localhost", "quibble_tests")
sender = "test@localhost"


def setup_func():
    Answer.objects.all().delete()
    q = queue.Queue(email('run/work'))
    q.clear()

def teardown_func():
    pass

@with_setup(setup_func, teardown_func)
def test_talking():

    """
    This message should move the state into
    TALKING.
    """

    msg = MailRequest('fakepeer', sender, "talk@mr.quibbl.es", open(home("tests/data/emails/question.msg")).read())
    Router.deliver(msg)
    q = queue.Queue(email('run/work'))
    assert q.count() == 2, "Queue count is actually %s" % str(q.count())


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
    assert q.count() == 2, "Queue count is actually %s" % str(q.count())
    assert len(Answer.objects.all()) == 4, "Oops. There are actually %s answers in the db, expected 4." % str(len(Answer.objects.all()))

