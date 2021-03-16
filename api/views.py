from django.shortcuts import render, get_object_or_404
from .serializers import QuizSerializer, QuestionSerializer, QuizAssignSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import Quiz, Question, QuizAssign
import json
# Create your views here.


class QuizView(GenericAPIView):
    serializer_class = QuizSerializer

    def get(self, request, quiz_id):
        result = {}
        quiz = get_object_or_404(Quiz, id=quiz_id)
        serializer = self.serializer_class(quiz)
        questions = Question.objects.filter(quiz=quiz)
        ques_serializer = QuestionSerializer(questions, many=True)
        result['quiz_details'] = serializer.data
        result['quiz_questions'] = ques_serializer.data
        return Response(result)


class QuizCreateView(GenericAPIView):
    serializer_class = QuizSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizCreateResponseView(GenericAPIView):
    serializer_class = QuizAssignSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizGetResponseView(GenericAPIView):
    serializer_class = QuizAssignSerializer

    def get(self, request, quiz_id, user_id):
        quiz = get_object_or_404(QuizAssign, quiz=quiz_id, user=user_id)
        serializer = self.serializer_class(quiz)
        return Response(serializer.data)


class QuizMarksView(GenericAPIView):
    serializer_class = QuizAssignSerializer

    def get(self, request, quiz_id, user_id):
        quiz_assign = get_object_or_404(QuizAssign, quiz=quiz_id, user=user_id)
        serializer = self.serializer_class(quiz_assign)
        response = serializer.data['response']
        response = response.replace("'", '"')
        res_dict = json.loads(response)
        quiz = quiz_assign.quiz
        questions = Question.objects.filter(quiz=quiz)
        marks = 0
        for i in range(len(questions)):
            if questions[i].answer is None:
                if questions[i].text == res_dict[str(questions[i].id)]:
                    marks += questions[i].correct_marks
                else:
                    marks += questions[i].negative_marks
            elif questions[i].text == "":
                if str(questions[i].answer) == res_dict[str(questions[i].id)]:
                    marks += questions[i].correct_marks
                else:
                    marks += questions[i].negative_marks
            elif questions[i].answer == "" and questions[i].text == "":
                marks += 0
        QuizAssign.objects.filter(quiz=quiz_id, user=user_id).update(marks=marks)
        return Response({"quiz": quiz.id, "user": user_id, "marks": marks})
