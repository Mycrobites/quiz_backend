from .serializers import QuizSerializer, QuestionSerializer, QuizResponseSerializer
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Quiz, Question, AssignQuiz, QuizResponse
from authentication.models import User
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import json
import uuid

# Create your views here.


class QuizView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def get(self, request, quiz_id):
        result = {}
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            serializer = self.serializer_class(quiz)
            questions = Question.objects.filter(quiz=quiz)
            ques_serializer = QuestionSerializer(questions, many=True)
            questions = ques_serializer.data
            for i in range(len(questions)):
                try:
                    options = questions[i]['option'].replace("'", '"')
                    questions[i]['option'] = json.loads(options)
                    options = []
                    for j in range(len(questions[i]['option'])):
                        options.append({'key': j + 1, 'option': questions[i]['option'][str(j + 1)]})
                    questions[i]['option'] = options
                except:
                    if questions[i]['option'] == "":
                        questions[i]['option'] = []
            result['quiz_details'] = serializer.data
            result['quiz_questions'] = ques_serializer.data
            return Response(result)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizCreateView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        user = User.objects.get(id=data['creator'])
        print(user.role)
        if user.role == 'Teacher':
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"message": "You dont have permission"})


class QuizEditView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def put(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            data = request.data
            if quiz.creator == data['creator']:
                serializer = self.serializer_class(quiz, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"message": "You dont have permission"})
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
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        options = data['option']
        option = {}
        for i in range(len(options)):
            option[str(options[i]['key'])] = options[i]['option']
        data['option'] = str(option)
        try:
            quiz = Quiz.objects.get(id=data['quiz'])
            if quiz.creator.id == data['creator']:
                del data['creator']
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                question = serializer.data
                for i in range(len(question['option'])):
                    try:
                        options = question['option'].replace("'", '"')
                        question['option'] = json.loads(options)
                        options = []
                        for j in range(len(question['option'])):
                            options.append({'key': j + 1, 'option': question['option'][str(j + 1)]})
                        question['option'] = options
                    except:
                        if question['option'] == "":
                            question['option'] = []
                return Response(question)
            else:
                return Response({"message": "You dont have permission"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizQuestionEditView(GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            data = request.data.copy()
            options = data['option']
            option = {}
            for i in range(len(options)):
                option[str(options[i]['key'])] = options[i]['option']
            data['option'] = str(option)
            x = uuid.UUID(str(question.quiz)).hex
            quiz = Quiz.objects.get(id=x)
            if quiz.creator.id == data['creator']:
                del data['creator']
                serializer = self.serializer_class(question, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                question = serializer.data
                for i in range(len(question['option'])):
                    try:
                        options = question['option'].replace("'", '"')
                        question['option'] = json.loads(options)
                        options = []
                        for j in range(len(question['option'])):
                            options.append({'key': j + 1, 'option': question['option'][str(j + 1)]})
                        question['option'] = options
                    except:
                        if question['option'] == "":
                            question['option'] = []
                return Response(question)
            else:
                return Response({"message": "You don't have permission to edit this question"})
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
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            response = data['response']
            resp = {}
            for i in range(len(response)):
                resp[response[i]['key']] = response[i]['answer']
            data['response'] = str(resp)
            user = User.objects.get(id = data['user'])
            if user.role == "Student":
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                response = serializer.data
                for i in range(len(response['response'])):
                    try:
                        responses = response['response'].replace("'", '"')
                        response['response'] = json.loads(responses)
                        responses = []
                        for res in response['response']:
                            responses.append({'key': res, 'answer': response['response'][res]})
                        response['response'] = responses
                    except:
                        if response['response'] == "":
                            response['response'] = []
                return Response(response)
            else:
                return Response({"message":"Teacher can't attempt the quiz"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "User not found with given id"})


class QuizGetResponseView(GenericAPIView):
    serializer_class = QuizResponseSerializer
    permission_classes = [AllowAny]

    def get(self, request, quiz_id, user_id):
        try:
            Quiz.objects.get(id=quiz_id)
            try:
                use = User.objects.get(id=user_id)
                if use.role == 'Student':
                    try:
                        quiz_assign = QuizResponse.objects.get(quiz=quiz_id, user=user_id)
                        serializer = self.serializer_class(quiz_assign)
                        response = serializer.data
                        for i in range(len(response['response'])):
                            try:
                                responses = response['response'].replace("'", '"')
                                response['response'] = json.loads(responses)
                                responses = []
                                for res in response['response']:
                                    responses.append({'key': res, 'answer': response['response'][res]})
                                response['response'] = responses
                            except:
                                if response['response'] == "":
                                    response['response'] = []
                        return Response(response)
                    except ObjectDoesNotExist:
                        raise ValidationError({"message": "Quiz was not attempted by the student with given user id"})
                else:
                    return Response({"message":"This is only for student"})
            except ObjectDoesNotExist:
                raise ValidationError({"message": "User not found with the given id"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizMarksView(GenericAPIView):
    serializer_class = QuizResponseSerializer
    permission_classes = [AllowAny]

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
    serializer_class = QuizResponseSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            user = User.objects.get(id=data["user"])
            if user.role == 'Student':
                try:
                    AssignQuiz.objects.get(quiz_id=data["quiz"], user_id=data["user"])
                    return Response({"Student already added"})
                except ObjectDoesNotExist:
                    serializer = self.serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({"message": "Student has been added to the quiz"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "quiz can be assigned only to students"})
        except ObjectDoesNotExist:
            return Response({"message": "Some error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizCollection(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def get(self, request, userid):
        try:
            user = User.objects.get(id=userid)
            if user.role == "Teacher":
                self.queryset = Quiz.objects.filter(creator=user)
                serializer = self.serializer_class(self.queryset, many=True)
                return Response(serializer.data)
            else:
                resp = []
                self.queryset = AssignQuiz.objects.filter(user=user)
                for i in self.queryset:
                    obj = Quiz.objects.filter(id=i.quiz_id)
                    serializer = self.serializer_class(obj, many=True)
                    resp.append(serializer.data)
                return Response(resp)
        except ObjectDoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

class QuizCollection(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]

    def get(self, request, userid):
        try:
            user = User.objects.get(id=userid)
            if user.role == "Teacher":
                self.queryset = Quiz.objects.filter(creator=user)
                serializer = self.serializer_class(self.queryset, many=True)
                return Response(serializer.data)
            else:
                resp = []
                self.queryset = AssignQuiz.objects.filter(user=user)
                for i in self.queryset:
                    self.queryset = Quiz.objects.filter(id=i.quiz_id)
                    serializer = self.serializer_class(self.queryset, many=True)
                    resp.append(serializer.data)
                return Response(resp)
        except ObjectDoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
