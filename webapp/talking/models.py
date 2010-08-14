from django.db import models

    
class Conversation(models.Model):
    
    created_on = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)


class Moderated(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)


class Snip(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation)
    prompt = models.TextField(blank=True)
    partone = ForeignKey(Answer)
    parttwo = ForeignKey(Answer)
    moderated = ForeignKey(Moderated)
    



