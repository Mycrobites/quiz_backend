from django.shortcuts import render, get_object_or_404
from .serializers import QuizSerializer, QuestionSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import Quiz, Question
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
