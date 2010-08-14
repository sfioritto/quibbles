from django.db import models


class User(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=512, primary_key=True)

    
class Conversation(models.Model):
    
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)


class Snip(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation)
    prompt = models.TextField(blank=True) 

class Answer(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)


class Moderated(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)







