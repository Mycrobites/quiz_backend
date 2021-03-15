from django.contrib import admin
from .models import Quiz, Question, QuizAssign, Role
# Register your models here.

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAssign)
admin.site.register(Role)