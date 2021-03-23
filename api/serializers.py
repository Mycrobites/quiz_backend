from .models import *
from rest_framework import serializers
import jsonfield


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return Quiz.objects.create(**validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


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
