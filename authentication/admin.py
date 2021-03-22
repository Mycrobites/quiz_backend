from django.contrib import admin
from api.models import AssignQuiz
from authentication.models import User,userFromFile
# Register your models here.


@admin.register(User)


class UserAdmin(admin.ModelAdmin):
    list_display = ["id","username","role"]
admin.site.register(userFromFile)