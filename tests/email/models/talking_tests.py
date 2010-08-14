from nose.tools import *
from webapp.talking.models import User, Conversation, Answer, Snip, Moderated
from app.model.talking import *
from lamson.mail import MailResponse

sender = "test@localhost"

def setup_func():
    
    User.objects.all().delete()
    Conversation.objects.all().delete()
    Answer.objects.all().delete()
    Moderated.objects.all().delete()
    Snip.objects.all().delete()
    
def teardown_func():
    pass

def test_get_user():
    u = User(email='test@localhost')
    
    msg = MailResponse(To="talk@mr.quibbl.es", From="test@localhost", Subject="Mr. Quibbles wants to your input", Body='test')
    
    new_u = get_user(msg)
    
    assert new_u.email == u.email 
    

@with_setup(setup_func, teardown_func)
def test_get_answer_message():
    u = User()
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

    print get_answer_message(a2).Body
    assert len(get_answer_message(a2).Body.split(DELIMITER)) == 4, "NOT ENOUGH DELIMITERS!"
