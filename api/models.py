from django.db import models
from django.contrib.auth.models import User
import uuid
import jsonfield
# Create your models here.


class Quiz(models.Model):
    title = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    desc = models.TextField()
    starttime = models.DateTimeField(null=True,blank=True)
    duration = models.TimeField(null=True,blank=True)
    endtime = models.DateTimeField()

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    correct_marks = models.SmallIntegerField()
    negative_marks = models.SmallIntegerField()
    option = jsonfield.JSONField(blank=True, null= True)
    answer = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quiz} - {self.question}"

class AssignQuiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class QuizResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = jsonfield.JSONField(blank=True)
    marks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.quiz}"


class Role(models.Model):
    role_choices = (
        ("Student", "Student"),
        ("Teacher", "Teacher")
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=role_choices)

    def __str__(self):
        return f"{self.user} - {self.role}"
