from django.urls import path
from .views import *


urlpatterns = [
    path("create-quiz", QuizCreateView.as_view(), name="create-quiz"),
    path("get-quiz/<slug:quiz_id>", QuizView.as_view(), name="get-quiz"),
    path("edit-quiz/<slug:quiz_id>", QuizEditView.as_view(), name="edit-quiz"),
    path("create-question", QuizQuestionCreateView.as_view(), name="create-question"),
    path("edit-question/<slug:question_id>", QuizQuestionEditView.as_view(), name="edit-question"),
    path("create-response", QuizCreateResponseView.as_view(), name="create-response"),
    path("get-response/<slug:quiz_id>/<int:user_id>", QuizGetResponseView.as_view(), name="get-response"),
    path("get-quiz-marks/<slug:quiz_id>/<int:user_id>", QuizMarksView.as_view(), name="get-quiz-marks"),
    path("add-student", AssignStudent.as_view(), name="assign-quiz"),
    path("get-all-quizzes/<slug:userid>", QuizCollection.as_view(), name="all-quizzes"),
    path("postFeedback/", PostFeedback.as_view(), name="postfeedback"),
    path("check-quiz-assigned", CheckQuizAssigned.as_view(), name="check-quiz-assigned"),
]
