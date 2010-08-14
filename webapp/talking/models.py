from django.db import models


class User(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=512)

    
class Conversation(models.Model):
    
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    
    def get_last_snip(self):
        snips = self.snip_set.all()
        
        if len(snips) > 0:
            snips.order_by('-sequence')
            
            return snips[0]
        else:
            return None

class Snip(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(Conversation)
    prompt = models.TextField(blank=True)
    sequence = models.IntegerField()
    
    def get_response(self):
        moderated_answers = snip.moderated_set.all()
        
        if len(moderated_answers) == 0:
            answers = Snip.answers_set.all()
            
            if len(answers) == 0:
                return None
            else:
                return answers[0].text
        else:
            return moderated_answers[0]

class Answer(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)


class Moderated(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)







