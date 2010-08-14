from nose.tools import *
from webapp.talking.models import User, Conversation, Answer, Snip, Moderated
from app.model.talking import *

sender = "test@localhost"

def setup_func():
    u = User(email=sender)
    u.save()
    
    c = Conversation(user=u)
    c.save()
    
    s1 = Snip(conversation=c,prompt='Hello Mr. Quibbles',sequence=0)
    s1.save()
    
    a1 = Answer(snip=s1,text='Hello User.')
    a1.save()
    
    m1 = Moderated(snip=s1,text='moderated Hello User.')
    m1.save()
    
    s2 = Snip(conversation=c,prompt='Are you people?',sequence=1)
    s2.save()
    
    a2 = Answer(snip=s2)
    a2.save()

def teardown_func():
    pass

def test_get_user():
    pass

def test_get_answer_message():
    snips = User.objects.get(email=sender)
    
    assert len(get_answer_message(a2).Body.split(DELIMITER)) == 3, "NOT ENOUGH DELIMITERS!"
