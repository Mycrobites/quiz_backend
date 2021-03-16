from django.urls import path
from .views import *


urlpatterns = [
    path("getQuiz/<slug:quiz_id>", QuizView.as_view(), name="get-quiz"),
    path("createQuiz", QuizCreateView.as_view(), name="create-quiz"),
    path("getResponse/<slug:quiz_id>/<int:user_id>", QuizGetResponseView.as_view(), name="get-response"),
    path("createResponse", QuizCreateResponseView.as_view(), name="create-response"),
    path("getQuizMarks/<slug:quiz_id>/<int:user_id>", QuizMarksView.as_view(), name="get-quiz-marks"),
]