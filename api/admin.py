from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Quiz)

admin.site.register(Question)



@admin.register(AssignQuiz)
class AssignAdmin(admin.ModelAdmin):
    list_filter = ["quiz"]


admin.site.register(QuizResponse)

admin.site.register(FeedBack)
