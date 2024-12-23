from api.views import feedbackQuestionsapi
from django.contrib import admin
from .models import *
from django import forms
# Register your models here.


@admin.register(AddQuestion)
class AddQuestionAdmin(admin.ModelAdmin):
    list_display = ["quiz","question","createdOn"]
    list_filter = ["quiz"]

class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "creator"]
    list_filter = ["title"]

class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_display = ["question_type","question", "correct_marks", "negative_marks", "get_answer"]
    list_filter = ["quiz__title", "subject_tag", "topic_tag", "subtopic_tag", "dificulty_tag", "skill"]

    def get_answer(self, obj):
        if obj.answer is None:
            return obj.text
        elif obj.text == "":
            return obj.answer
        else:
            return None


    get_answer.short_description = 'Answer'


class AssignChangeForm(forms.ModelForm):

    class Meta:
        model= AssignQuizGroup
        fields = ('quiz_group','user_group')

class AssignAdmin(admin.ModelAdmin):
    form = AssignChangeForm
    model = AssignQuizGroup


class ResponseAdmin(admin.ModelAdmin):
    model = QuizResponse
    list_display = ["get_user", "get_quiz", "marks_obtained"]
    list_filter = ["quiz__title", "user"]

    def get_user(self, obj):
        return f"{obj.user}'s response"

    def get_quiz(self, obj):
        return obj.quiz.title

    get_user.short_description = "User's Response"
    get_quiz.short_description = "Quiz"


class FeedbackAdmin(admin.ModelAdmin):
    model = FeedBackForm
    list_display = ['get_user', 'get_quiz']
    list_filter = ['quiz_id__title']

    def get_user(self, obj):
        return obj.user.username

    def get_quiz(self, obj):
        return obj.quiz_id.title

    get_quiz.short_description = 'Quiz'
    get_user.short_description = 'Username'

class SaveResultAdmin(admin.ModelAdmin):
    list_display = ['user','name', 'quizname',]
    list_filter = ['quizname',]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizGroup)
admin.site.register(AssignQuizGroup, AssignAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizResponse, ResponseAdmin)
admin.site.register(FeedBackForm, FeedbackAdmin)
admin.site.register(UserQuizSession)
admin.site.register(save_result, SaveResultAdmin)
admin.site.register(feedbackQuestions)
admin.site.register(run_excel_task)
admin.site.register(QuizQuestion)
