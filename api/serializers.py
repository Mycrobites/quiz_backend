from .models import Quiz, Question, QuizAssign
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


class QuizAssignSerializer(ModelSerializer):

    class Meta:
        model = QuizAssign
        fields = "__all__"
