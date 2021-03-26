from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Quiz)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_filter = ["quiz"]
    list_display= ["quiz","question","correct_marks","negative_marks","answer"]


@admin.register(AssignQuiz)
class AssignAdmin(admin.ModelAdmin):
    list_filter = ["quiz"]


@admin.register(QuizResponse)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ["quiz", "user", "marks"]
    list_filter = ["user", "quiz"]


admin.site.register(FeedBackForm)
admin.site.register(UserQuizSession)