from django.contrib import admin
from .models import *

# Register your models here.


class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "creator"]
    list_filter = ["title"]


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_filter = ["quiz", "subject_tag", "topic_tag", "subtopic_tag", "dificulty_tag", "skill"]
    list_display = ["quiz", "question", "correct_marks", "negative_marks", "get_answer"]

    def get_answer(self, obj):
        if obj.answer is None:
            return obj.text
        elif obj.text == "":
            return obj.answer
        else:
            return None

    get_answer.short_description = 'Answer'


class AssignAdmin(admin.ModelAdmin):
    list_filter = ["quiz"]


class ResponseAdmin(admin.ModelAdmin):
    list_display = ["get_user", "quiz", "marks"]
    list_filter = ["quiz", "user"]

    def get_user(self, obj):
        return f"{obj.user}'s response"

    get_user.short_description = "User's Response"


class FeedbackAdmin(admin.ModelAdmin):
    model = FeedBackForm
    list_display = ['get_user', 'get_quiz']
    list_filter = ['quiz_id']

    def get_user(self, obj):
        return obj.user.username

    def get_quiz(self, obj):
        return obj.quiz_id

    get_quiz.short_description = 'Quiz'
    get_user.short_description = 'Username'


admin.site.register(Quiz, QuizAdmin)
admin.site.register(AssignQuiz, AssignAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizResponse, ResponseAdmin)
admin.site.register(FeedBackForm, FeedbackAdmin)
admin.site.register(UserQuizSession)
