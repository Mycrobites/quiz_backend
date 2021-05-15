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
    desc = models.TextField()
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


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = RichTextUploadingField()
    correct_marks = models.PositiveSmallIntegerField()
    negative_marks = models.PositiveSmallIntegerField()
    option = jsonfield.JSONField(blank=True, null=True)
    answer = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(blank=True)
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


choice = (
    ("yes", "yes"),
    ("no", "no"),
)

choice_contest = (
    ("Puzzle Solving", "Puzzle Solving"),
    ("Problem solving strategies", "Problem solving strategies"),
    ("Mental Maths", "Mental Maths"),
    ("Mathematics to entertain your spirit", "Mathematics to entertain your spirit"),
)


class FeedBackForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE, default="4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f")
    learn_new = models.PositiveIntegerField()
    like_participating = models.PositiveIntegerField()
    difficulty = models.PositiveSmallIntegerField()
    participate_again = models.CharField(max_length=5, choices=choice)
    time_sufficient = models.CharField(max_length=5, choices=choice)
    attend_webinar = models.CharField(max_length=5, choices=choice)
    language_english = models.CharField(max_length=5, choices=choice)
    mini_course = models.CharField(max_length=5, choices=choice)
    next_contest = models.CharField(max_length=150, choices=choice_contest)
    suggestions = models.CharField(max_length=200, default="")
    username = models.CharField(max_length=60, default="")

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