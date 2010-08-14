from config import testing
from nose.tools import *
from lamson.testing import *
from lamson.routing import Router
from lamson.mail import MailRequest
from lamson import queue
from conf import *


relay = relay(port=8823)
client = RouterConversation("somedude@localhost", "quibble_tests")
sender = "test@localhost"


def setup_func():
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

