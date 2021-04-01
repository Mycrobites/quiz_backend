from djongo import models
from authentication.models import User
import uuid
import jsonfield
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from datetime import datetime


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
        return str(self.title)

    def is_active(self, time):
        if self.endtime > time:
            return True
        else:
            return False


dificulty_choices = (
    ("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")
)


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
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
        return f"{self.quiz} - {self.question}"


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

    def save(self, *args, **kwargs):

        feedbacks = FeedBackForm.objects.all()
        data = pd.read_csv("media/feedback/Feedback - Sheet1.csv")
        data.fillna("NA", inplace=True)

        for i in range(len(feedbacks)):
            data.loc[i , "User"] = feedbacks[i].user
            data.loc[i , "Quiz ID"] = feedbacks[i].quiz_id
            data.loc[i , "Learn New"] = feedbacks[i].learn_new
            data.loc[i , "Like Participating"] = feedbacks[i].like_participating
            data.loc[i , "Difficulty"] = feedbacks[i].difficulty
            data.loc[i , "Participate Again"] = feedbacks[i].participate_again
            data.loc[i , "Time Sufficient"] = feedbacks[i].time_sufficient
            data.loc[i , "Attend Webinar"] = feedbacks[i].attend_webinar
            data.loc[i , "Language English"] = feedbacks[i].language_english
            data.loc[i , "Mini Course"] = feedbacks[i].mini_course
            data.loc[i , "Next Contest"] = feedbacks[i].next_contest
            data.loc[i , "Suggestions"] = feedbacks[i].suggestions
            data.loc[i , "Username"] = feedbacks[i].username

        filename = "media/feedbackResponses/output.csv"
        data.to_csv(filename)
        super(FeedBackForm, self).save(*args, **kwargs)


class UserQuizSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE, default="4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f")
    start_time = models.DateTimeField(null=True, blank=True, default=datetime.now)
    remaining_duration = models.TimeField(null=True, blank=True)


# class FeedBackResponseFile(models.Model):
#     id = models.AutoField(primary_key=True)
#     feedbackdata = models.FileField(upload_to="feedbackdata", max_length=1000)
#     filename = models.CharField(max_length=100,default="output.csv",blank=True)

#     def save(self, *args, **kwargs):
#         data = pd.read_csv(self.feedbackdata)
#         data.fillna("NA", inplace=True)
#         for i in range(data.shape[0]):

#             user = data.iloc[i]["User"]
#             quiz_id = data.iloc[i]["Quiz ID"]
#             learn_new =  data.iloc[i]["Learn New"]
#             like_participating =  data.iloc[i]["Like Participating"]
#             difficulty =  data.iloc[i]["Difficulty"]
#             participate_again =  data.iloc[i]["Participate Again"]
#             time_sufficient = data.iloc[i]["Time Sufficient"]
#             attend_webinar =  data.iloc[i]["Attend Webinar"]
#             language_english =  data.iloc[i]["Language English"]
#             mini_course = data.iloc[i]["Mini Course"]
#             next_contest = data.iloc[i]["Next Contest"]
#             suggestions =  data.iloc[i]["Suggestions"]
#             username = data.iloc[i]["Username"]

#             FeedBackForm.objects.create(user=user,quiz_id=quiz_id,learn_new=learn_new,like_participating=like_participating,
#                                 difficult=difficulty,participate_again=participate_again,time_sufficient=time_sufficient,attend_webinar=attend_webinar,
#                                 language_english=language_english,mini_course=mini_course,next_contest=next_contest,suggestions=suggestions,username=username)
  
#         self.filename = "media/feedbackResponces/"+"details"+str(get_random_string(length=5)) + ".csv"
#         data.to_csv(self.filename)
#         super(FeedBackResponseFile, self).save(*args, **kwargs)
