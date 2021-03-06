from nose.tools import *
from webapp.talking.models import User, Conversation, Answer, Snip, Moderated
from app.model.talking import *
from lamson.mail import MailResponse, MailRequest

sender = "test@localhost"

def setup_func():
    
    User.objects.all().delete()
    Conversation.objects.all().delete()
    Answer.objects.all().delete()
    Moderated.objects.all().delete()
    Snip.objects.all().delete()
    
def teardown_func():
    pass

@with_setup(setup_func, teardown_func)
def test_get_user():
    u = User(email='test@localhost')
    
    msg = MailResponse(To="talk@mr.quibbl.es", From="test@localhost", Subject="Mr. Quibbles wants to your input", Body='test')
    
    new_u = get_user(msg)
    
    assert new_u.email == u.email 

@with_setup(setup_func, teardown_func)    
def test_find_users():
    address = 'test@localhost'
    address2 = 'test2@localhost'
    
    u1 = User(email=address)
    u1.save()
    
    u2 = User(email=address2)
    u2.save()
    
    found_user = find_user(address)
    
    assert address == found_user.email
    
    User.objects.all().delete()
    
    assert find_user(address) == None

@with_setup(setup_func, teardown_func)
def test_create_conv():
    u = User(email='test@localhost')
    u.save()
    
    conv = create_conversation(u)
    
    assert len(u.conversation_set.all()) == 1, "Incorrect number of conversations: " + str(len(u.conversation_set.all()))

@with_setup(setup_func, teardown_func)
def test_scrape_response():
    body = 'test' + DELIMITER + 'test2'
    msg = MailResponse(To="talk@mr.quibbl.es", From="test@localhost", Subject="Mr. Quibbles wants to your input", Body=body)
    
    assert scrape_response(msg.Body) == 'test'
    
    body = ''
    msg = MailResponse(To="talk@mr.quibbl.es", From="test@localhost", Subject="Mr. Quibbles wants to your input", Body=body)
    
    assert scrape_response(msg.Body) == ''

@with_setup(setup_func, teardown_func)
def test_create_snip():
    body = 'test' + DELIMITER + 'test2'
    msg = MailRequest('fakepeer', "test@localhost", "talk@mr.quibbl.es", body)
    u = User(email="test@localhost")
    u.save()
    
    conv = Conversation(user=u)
    conv.save()
    
    snip = create_snip(msg, conv)
    
    assert len(conv.snip_set.all()) == 1

@with_setup(setup_func, teardown_func)
def test_get_snip_sequence():
    body = 'test' + DELIMITER + 'test2'
    msg = MailRequest('fakepeer', "test@localhost", "talk@mr.quibbl.es", body)
    u = User(email="test@localhost")
    u.save()
    
    conv = Conversation(user=u)
    conv.save()
    
    assert get_snip_sequence(conv) == 0
    
    snip = create_snip(msg, conv)
    
    assert get_snip_sequence(conv) == 1

@with_setup(setup_func, teardown_func)
def test_create_mod_response_message():
    u = User()
    u.save()
    
    c = Conversation(user=u)
    c.save()
    
    s1 = Snip(conversation=c,prompt='Hello Mr. Quibbles',sequence=0,complete=True)
    s1.save()
    
    a1 = Answer(snip=s1,text='Hello User.')
    a1.save()
    
    m1 = Moderated(snip=s1,text='moderated Hello User.')
    m1.save()
    
    s2 = Snip(conversation=c,prompt='Are you people?',sequence=1,complete=True)
    s2.save()
    
    a2 = Answer(snip=s2,text='Skynet is people.')
    a2.save()
    
    mod_message = build_response_message_body(s2)

@with_setup(setup_func, teardown_func)
def test_build_moderation_request_message_body():
    u = User()
    u.save()
    
    c = Conversation(user=u)
    c.save()
    
    s1 = Snip(conversation=c,prompt='Hello Mr. Quibbles',sequence=0,complete=True)
    s1.save()
    
    a1 = Answer(snip=s1,text='Hello User.')
    a1.save()
    
    m1 = Moderated(snip=s1,text='moderated Hello User.')
    m1.save()
    
    s2 = Snip(conversation=c,prompt='Are you people?',sequence=1)
    s2.save()
    
    a2 = Answer(snip=s2,text='Skynet is people.')
    a2.save()
    a3 = Answer(snip=s2,text='I am Skynet.')
    a3.save()
    
    moderation_request_message = build_mod_request_message_body(s2)

@with_setup(setup_func, teardown_func)
def test_get_answer_message():
    u = User()
    u.save()
    
    c = Conversation(user=u)
    c.save()
    
    s1 = Snip(conversation=c,prompt='Hello Mr. Quibbles',sequence=0,complete=True)
    s1.save()
    
    a1 = Answer(snip=s1,text='Hello User.')
    a1.save()
    
    m1 = Moderated(snip=s1,text='moderated Hello User.')
    m1.save()
    
    s2 = Snip(conversation=c,prompt='Are you people?',sequence=1)
    s2.save()
    
    a2 = Answer(snip=s2)
    a2.save()

    answer_message = get_answer_message(a2)
