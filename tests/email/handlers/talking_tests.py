from nose.tools import *
from lamson.testing import *
from lamson.routing import Router
from lamson.mail import MailRequest
from lamson import queue


relay = relay(port=8823)
client = RouterConversation("somedude@localhost", "quibble_tests")
sender = "test@localhost"


def setup_func():
    pass

def teardown_func():
    pass

@with_setup(setup_func, teardown_func)
def test_talking(msg=None):

    """
    This message should move the state into
    TALKING.
    """
    assert True
