from djongo import models
from authentication.models import User
import uuid
import jsonfield


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

    def __str__(self):
        return str(self.title)+" "+str(self.creator.username)

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    correct_marks = models.SmallIntegerField()
    negative_marks = models.SmallIntegerField()
    option = jsonfield.JSONField(blank=True, null=True)
    answer = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quiz} - {self.question}"


class AssignQuiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    user = models.ManyToManyField(User,)

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

class FeedBack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_question = models.PositiveSmallIntegerField()
    interface = models.PositiveSmallIntegerField()
    difficulty = models.PositiveSmallIntegerField()

