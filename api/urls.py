from django.urls import path
from .views import *


urlpatterns = [
    path("getQuiz/<slug:quiz_id>", QuizView.as_view()),
    path("createQuiz", QuizCreateView.as_view()),
]