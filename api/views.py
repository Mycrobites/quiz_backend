from .serializers import *
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import json
# Create your views here.

class QuizCollection(GenericAPIView):
    serializer_class = QuizSerializer
    
    def get(self,request,userid):
        #try:
            userobj = User.objects.get(id=userid)
            if(userobj.role.role=="Teacher"):
                obj = Quiz.objects.filter(creator=userobj)
                serializer = self.serializer_class(obj,many=True)
                return Response(serializer.data)
            else:
                resp = []
                assignobj = AssignQuiz.objects.filter(user=userobj)
                for i in assignobj:
                    obj = Quiz.objects.filter(id=i.quiz_id)
                    serializer = self.serializer_class(obj,many=True)
                    resp.append(serializer.data)
                return Response(resp)
        # except:
        #     return Response({"message":"User does not exist"},status=status.HTTP_404_NOT_FOUND)


class QuizView(GenericAPIView):
    serializer_class = QuizSerializer

    def get(self, request, quiz_id):
        result = {}
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            serializer = self.serializer_class(quiz)
            questions = Question.objects.filter(quiz=quiz)
            ques_serializer = QuestionSerializer(questions, many=True)
            result['quiz_details'] = serializer.data
            result['quiz_questions'] = ques_serializer.data
            return Response(result)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizCreateView(GenericAPIView):
    serializer_class = QuizSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizEditView(GenericAPIView):
    serializer_class = QuizSerializer

    def put(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            data = request.data
            serializer = self.serializer_class(quiz, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})

    def delete(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.delete()
            return Response({"message": "Quiz deleted successfully"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizQuestionCreateView(GenericAPIView):
    serializer_class = QuestionSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizQuestionEditView(GenericAPIView):
    serializer_class = QuestionSerializer

    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            data = request.data
            serializer = self.serializer_class(question, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Question not found with the given id"})

    def delete(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Question not found with the given id"})


class QuizCreateResponseView(GenericAPIView):
    serializer_class = QuizResponseSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizGetResponseView(GenericAPIView):
    serializer_class = QuizResponseSerializer

    def get(self, request, quiz_id, user_id):
        try:
            Quiz.objects.get(id=quiz_id)
            try:
                User.objects.get(id=user_id)
                try:
                    quiz_assign = QuizResponse.objects.get(quiz=quiz_id, user=user_id)
                    serializer = self.serializer_class(quiz_assign)
                    return Response(serializer.data)
                except ObjectDoesNotExist:
                    raise ValidationError({"message": "Quiz was not attempted by the student with given user id"})
            except ObjectDoesNotExist:
                raise ValidationError({"message": "User not found with the given id"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizMarksView(GenericAPIView):
    serializer_class = QuizResponseSerializer

    def get(self, request, quiz_id, user_id):
        try:
            Quiz.objects.get(id=quiz_id)
            try:
                User.objects.get(id=user_id)
                try:
                    quiz_assign = QuizResponse.objects.get(quiz=quiz_id, user=user_id)
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
                    QuizResponse.objects.filter(quiz=quiz_id, user=user_id).update(marks=marks)
                    return Response({"quiz": quiz.id, "user": user_id, "marks": marks})
                except ObjectDoesNotExist:
                    raise ValidationError({"message": "Quiz was not attempted by the student with given user id"})
            except ObjectDoesNotExist:
                raise ValidationError({"message": "User not found with the given id"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class AssignStudent(GenericAPIView):
    serializer_class = AssignQuizSerializer

    def post(self,request):
        try:
            data = request.data
            try:
                AssignQuiz.objects.get(quiz_id=data["quiz"],user_id=data["user"])
                return Response({"Student already added"})
            except:
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message":"Student has been added to the quiz"},status=status.HTTP_200_OK)
        except:
            return Response({"message":"Some error occured"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


