from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path("create-quiz-group",QuizGroupCreateView.as_view(), name="create-quiz-group"),
    path("create-quiz", QuizCreateView.as_view(), name="create-quiz"),
    path("get-quiz/<slug:quiz_id>", QuizView.as_view(), name="get-quiz"),
    path("edit-quiz/<slug:quiz_id>", QuizEditView.as_view(), name="edit-quiz"),
    path("create-question", QuizQuestionCreateView.as_view(), name="create-question"),
    path("edit-question/<slug:question_id>", QuizQuestionEditView.as_view(), name="edit-question"),
    path("create-response", QuizCreateResponseView.as_view(), name="create-response"),
    path("get-response/<slug:quiz_id>/<int:user_id>", QuizGetResponseView.as_view(), name="get-response"),
    path("get-quiz-marks/<slug:quiz_id>/<int:user_id>", QuizMarksView.as_view(), name="get-quiz-marks"),
    path("add-student", AssignStudent.as_view(), name="assign-quiz"),
    path("add-group", AssignGroup.as_view(), name="assign-quiz-groups"),
    path("get-all-quizzes/<slug:userid>", QuizCollection.as_view(), name="all-quizzes"),
    path("Feedback/", createFeedback.as_view(), name="createFeedback"),
    path("check-quiz-assigned", CheckQuizAssigned.as_view(), name="check-quiz-assigned"),
    path("userSession/", PostUserQuizSession.as_view(), name="userquizsesion"),
    path("getUserSession/<slug:pk>", GetUserQuizSession.as_view(), name="getuserquizsesion"),
    path("filterscore",views.filterscore,name="filterscore"),
    path("result",views.result,name="result"),
    path("resultanalysis",views.resultanalysis,name="resultanalysis"),
    path("getresult/<str:username>/<str:quizid>", views.GetResult.as_view()),
    path("requestExcelForResult", views.RunExcelCreateView.as_view()),
    path("requestScoreForResult/<str:quizid>", views.getScorecard.as_view()),
    path("getExcelForResult", views.CreateExcelForScore.as_view()),
    path('getQuestionsFromQB/<str:quizid>', QuestionBankListView.as_view()),
    path('addQuestionToQuiz', AddQuestionToQuiz.as_view()),
    path('deleteQuestionFromQuiz/<slug:quiz_id>/<slug:question_id>', DeleteQuestionFromQuiz.as_view()),
    path('FeedbackQs/post',feedbackQuestionsapi().as_view()),
    path('FeedbackQs/<slug:quiz_id>/get',feedbackQuestionsapi().as_view()),
    path('FeedbackQs/<slug:question_id>/patch',feedbackQuestionsapi().as_view()),
    path('checkForResult',views.check_for_result,name="check_for_result"),
    path('getstudentresult/<str:userid>', get_student_result.as_view()),
    path('getstudentreport/<str:id>', get_student_report.as_view())
# get_student_result
]
