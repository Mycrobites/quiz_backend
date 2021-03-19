from .models import *
from rest_framework.serializers import ModelSerializer


class QuizSerializer(ModelSerializer):

    class Meta:
        model = Quiz
        fields = "__all__"
    
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return Quiz.objects.create(**validated_data)


class QuestionSerializer(ModelSerializer):

    class Meta:
        model = Question
        fields = "__all__"


class QuizResponseSerializer(ModelSerializer):

    class Meta:
        model = QuizResponse
        fields = "__all__"

class AssignQuizSerializer(ModelSerializer):

    class Meta:
        model = AssignQuiz
        fields = "__all__"