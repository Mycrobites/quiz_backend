from django.contrib import admin
from .models import *
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
    list_display = ["question", "correct_marks", "negative_marks", "get_answer"]
    list_filter = ["quiz__title", "subject_tag", "topic_tag", "subtopic_tag", "dificulty_tag", "skill"]

    def get_answer(self, obj):
        if obj.answer is None:
            return obj.text
        elif obj.text == "":
            return obj.answer
        else:
            return None


    get_answer.short_description = 'Answer'


class AssignAdmin(admin.ModelAdmin):
    model = AssignQuiz
    list_display = ["get_quiz"]
    list_filter = ["quiz__title"]

    def get_quiz(self, obj):
        return obj.quiz.title

    get_quiz.short_description = "Quiz"


class ResponseAdmin(admin.ModelAdmin):
    model = QuizResponse
    list_display = ["get_user", "get_quiz", "marks"]
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


admin.site.register(Quiz, QuizAdmin)
admin.site.register(AssignQuiz, AssignAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizResponse, ResponseAdmin)
admin.site.register(FeedBackForm, FeedbackAdmin)
admin.site.register(UserQuizSession)
