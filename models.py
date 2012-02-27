from django.db import models
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect

# Create your models here.
class QuizProfile(models.Model):
    total_score = models.FloatField("Total score")
    total_time = models.FloatField("Total time spent on questions", default=0.0)
    total_attempts = models.IntegerField("Total attempts", default=0)
    fb_share_key = models.CharField(max_length=500)
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.user.username   

    class Meta:
        ordering = ['-user'] 
        get_latest_by = 'time'

    def update(self):
        aqs = AttemptedQuestion.objects.all().filter(player=self)
        self.total_score = 0.0
        self.total_time = 0.0
        self.total_attempts = int(str(aqs.count()),10)
        for a in aqs:
            self.total_score += a.marks_obtained
            self.total_time += a.time_taken
        self.save()
        

class Question(models.Model):
    OPTIONS = (
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4'),
    )
        
    title = models.TextField("Question",)
    author = models.ForeignKey(User)
    option1 = models.CharField("Option 1", max_length=100, help_text = "Please enter first choice")
    option2 = models.CharField("Option 2", max_length=100, help_text = "Please enter second choice")
    option3 = models.CharField("Option 3", max_length=100, help_text = "Please enter third choice")
    option4 = models.CharField("Option 4", max_length=100, help_text = "Please enter fourth Choice")
    correct_option = models.IntegerField("Correct Option", choices = OPTIONS, help_text = "Please Choose Correct Answer")
    max_marks = models.IntegerField("Maximum Marks", default = 10, help_text = "Maximum marks will be in whole number.<br>If time spent is more than Minimum time.<br><i><strong>Marks obtained = Maximum marks*Minimum time/Actual time taken.</strong></i>" )
    min_time = models.FloatField("Minimum Time", default = 8.0, help_text = "Please enter minimum time in seconds.")
    max_time = models.FloatField("Maximum Time", default = 600.0, help_text = "Please enter maximum time in seconds. Automatic timeout after this much time.")
    
    
    def __unicode__(self):
        return self.title
    
class AttemptedQuestion(models.Model):
    question = models.ForeignKey(Question)
    player = models.ForeignKey(QuizProfile)
    answered = models.BooleanField(default=False)
    time_taken = models.FloatField(default=0)
    server_time_taken = models.FloatField(default=0)
    time = models.DateTimeField(auto_now_add = True)
    marks_obtained = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-time']
        get_latest_by = 'time'
    
    def __unicode__(self):
        return "Answer by -> " + self.player.user.username+ " for question number " + str(self.question.id) + " obtained marks - " + str(self.marks_obtained)
    
