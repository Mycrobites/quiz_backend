from django.db import models
from django.contrib.auth.models import User
import uuid
import jsonfield
# Create your models here.


class Quiz(models.Model):
    title = models.CharField(max_length=50)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    desc = models.TextField()
    endtime = models.DateTimeField()

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    correct_marks = models.SmallIntegerField()
    negative_marks = models.SmallIntegerField()
    answer = models.PositiveSmallIntegerField()
    option = jsonfield.JSONField()
    text = models.TextField()

class QuizAssign(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)