from djongo import models
from authentication.models import User
import uuid
import jsonfield
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
from datetime import date
from django.utils import timezone


# Create your models here.


class Quiz(models.Model):
    title = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    instructions = RichTextUploadingField()
    desc = RichTextUploadingField()
    starttime = models.DateTimeField(null=True, blank=True)
    duration = models.TimeField(null=True, blank=True)
    endtime = models.DateTimeField()
    question = models.ManyToManyField("Question",null=True,blank=True)
    quesorder = models.CharField(max_length=1000000,blank=True,default="[]")


    def __str__(self):
        return str(self.title)

    def is_active(self, time):
        if self.endtime > time and self.starttime < time:
            return True
        else:
            return False


dificulty_choices = (
    ("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")
)

class AddQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    createdOn = models.DateTimeField(default=timezone.now())

question_type_Choices = (
    ("Multiple Correct","Multiple Correct"),
    ( "True False","True False"),
    ("Matching","Matching"),
    ("Input Type","Input Type"),
    ("Single Correct","Single Correct"),
    ("Assertion Reason","Assertion Reason"))

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_type=models.CharField(choices=question_type_Choices, blank=True, default="", max_length=100)
    passage= RichTextUploadingField()#to be used for assertion/and reason type
    question = RichTextUploadingField()
    correct_marks = models.PositiveSmallIntegerField()
    negative_marks = models.PositiveSmallIntegerField()
    option = jsonfield.JSONField(blank=True, null=True)
    answer = jsonfield.JSONField(blank=True, null=True)
    text = jsonfield.JSONField(blank=True, null=True)
    subject_tag = models.CharField(max_length=100, blank=True, default="")
    topic_tag = models.CharField(max_length=100, blank=True, default="")
    subtopic_tag = models.CharField(max_length=100, blank=True, default="")
    dificulty_tag = models.CharField(choices=dificulty_choices, blank=True, default="", max_length=100)
    skill = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.question[:250]


class AssignQuiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    user = models.ManyToManyField(User, )

    def __str__(self):
        return str(self.quiz)


class QuizResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = jsonfield.JSONField(blank=True)
    marks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user}'s response on {self.quiz}"

class feedbackQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE, default="4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f")
    question=jsonfield.JSONField(blank=True, null=True)
    def __str__(self):
        return f"{self.user}'s Question for{self.quiz_id}"

class FeedBackForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE, default="4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f")
    answer=jsonfield.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}'s feedback"

  
class UserQuizSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE, default="4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f")
    start_time = models.DateTimeField(null=True, blank=True, default=datetime.now)
    remaining_duration = models.TimeField(null=True, blank=True)

    def ___str___(self):
        return f"{self.user}'s remaining time is {self.remaining_duration}"

def upload_and_Rename(instance,filename):
    datea = str(date.today())
    year,month,datea = datea.split("-")
    upload_to = "uploads/"+str(year)+"/"+str(month)+"/"+str(datea)+"/"+filename
    return upload_to

class upload_image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(upload_to=upload_and_Rename, height_field=None, width_field=None, max_length=None)

class run_excel_task(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    quizid=models.CharField(max_length=150,null=False)
    email_send=models.EmailField(max_length=254,null=False)

class save_result(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    quizid=models.CharField(max_length=150,null=False)
    quizname=models.CharField(max_length=50,null=True)
    name=models.CharField(max_length=50,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    score=models.CharField(max_length=5,null=False)
    rank=models.CharField(max_length=5,null=True)
    data = jsonfield.JSONField(blank=True)