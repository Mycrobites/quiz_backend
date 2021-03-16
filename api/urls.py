from django.urls import path
from .views import *


urlpatterns = [
    path("getQuiz/<slug:quiz_id>", QuizView.as_view()),
    path("createQuiz", QuizCreateView.as_view()),
    path("getResponse/<slug:quiz_id>/<int:user_id>", QuizResponseView.as_view()),
    path("getQuizMarks/<slug:quiz_id>/<int:user_id>", QuizMarksView.as_view()),
]