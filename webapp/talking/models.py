from django.db import models


class User(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    karma = models.IntegerField(default=0)
    email = models.CharField(max_length=512,unique=True)

    def enough_karma(self):
        return self.karma >= 2

    def add_karma(self, work_count=None):
        if work_count == None:
            self.karma += 1
        else:
            self.karma += 2 - work_count
        
        self.save()

    def use_karma(self):
        assert self.karma <= 2, "Not enough karma to use."
        self.karma = self.karma - 2
        self.save()

    
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
    complete = models.BooleanField()

    def ready_to_moderate(self):
        return len(self.answer_set.all())
    
    def get_response(self):
        moderated_answers = self.moderated_set.all()
        
        if len(moderated_answers) == 0:
            answers = self.answer_set.all()
            
            if len(answers) == 0:
                return "Hmmm... I'm not sure I know enough to say anything meaningful here."
            else:
                return answers[0].text
        else:
            return moderated_answers[0].text

class Answer(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)


class Moderated(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    snip = models.ForeignKey(Snip)







