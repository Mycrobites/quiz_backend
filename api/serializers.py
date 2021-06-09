from .models import *
from rest_framework import serializers
import jsonfield


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id","quizgroup","title","creator","starttime","endtime","duration","instructions","desc"]

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return Quiz.objects.create(**validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['answer']


class QuizResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResponse
        fields = "__all__"


class AssignQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignQuiz
        fields = "__all__"


class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBackForm
        fields = "__all__"

class FeedbackQuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = feedbackQuestions
        fields = "__all__"


class UserQuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizSession
        fields = "__all__"

class RunExcelTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = run_excel_task
        fields = "__all__"
