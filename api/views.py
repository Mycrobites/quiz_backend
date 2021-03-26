from .serializers import *
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import *
from authentication.models import User
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import json
# from datetime import datetime
import datetime

# Create your views here.


class QuizView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, quiz_id):
        result = {}
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.is_active(timezone.now()):
                serializer = self.serializer_class(quiz)
                questions = Question.objects.filter(quiz=quiz)
                ques_serializer = QuestionSerializer(questions, many=True)
                questions = ques_serializer.data
                for i in range(len(questions)):
                    flag = False
                    string = questions[i]["question"]
                    for j in range(len(string)):
                        if string[j]== "s" and string[j + 1]== "r"and string[j + 2]== "c"and string[j + 3]== "=":
                            flag=True
                            string = string[:j+5]+"https://quiz-mycrobites.herokuapp.com"+string[j+5:]
                    questions[i]["question"] = string
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
            else:
                return Response({"message": "This quiz is closed now"}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizCreateView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizEditView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        options = data['option']
        option = {}
        for i in range(len(options)):
            option[str(options[i]['key'])] = options[i]['option']
        data['option'] = str(option)
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


class QuizQuestionEditView(GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            data = request.data
            options = data['option']
            option = {}
            for i in range(len(options)):
                option[str(options[i]['key'])] = options[i]['option']
            data['option'] = str(option)
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        user_id = request.data['user']
        quiz_id = request.data['quiz']
        try:
            QuizResponse.objects.get(quiz=quiz_id, user=user_id)
            return Response({"message": "You have already attempted the quiz"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            response = data['response']
            resp = {}
            for i in range(len(response)):
                resp[response[i]['key']] = response[i]['answer']
            data['response'] = str(resp)
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = serializer.data
            res_dict = json.loads(response['response'].replace("'", '"'))
            quiz = Quiz.objects.get(id=quiz_id)
            questions = Question.objects.filter(quiz=quiz)
            marks = 0
            for i in range(len(questions)):
                if questions[i].answer is None:
                    if questions[i].text == res_dict[str(questions[i].id)]:
                        marks += questions[i].correct_marks
                    else:
                        marks -= questions[i].negative_marks
                elif questions[i].text == "":
                    if str(questions[i].answer) == res_dict[str(questions[i].id)]:
                        marks += questions[i].correct_marks
                    else:
                        marks -= questions[i].negative_marks
                elif questions[i].answer == "" and questions[i].text == "":
                    marks += 0
            QuizResponse.objects.filter(quiz=quiz_id, user=user_id).update(marks=marks)
            response_id = response["id"]
            quiz_response = QuizResponse.objects.get(id=response_id)
            serializer = self.serializer_class(quiz_response)
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


class QuizGetResponseView(GenericAPIView):
    serializer_class = QuizResponseSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, quiz_id, user_id):
        try:
            Quiz.objects.get(id=quiz_id)
            try:
                User.objects.get(id=user_id)
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
            except ObjectDoesNotExist:
                raise ValidationError({"message": "User not found with the given id"})
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizMarksView(GenericAPIView):
    serializer_class = QuizResponseSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
                                marks -= questions[i].negative_marks
                        elif questions[i].text == "":
                            if str(questions[i].answer) == res_dict[str(questions[i].id)]:
                                marks += questions[i].correct_marks
                            else:
                                marks -= questions[i].negative_marks
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data
            try:
                AssignQuiz.objects.get(quiz_id=data["quiz"], user_id=data["user"])
                return Response({"Student already added"})
            except ObjectDoesNotExist:
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "Student has been added to the quiz"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Some error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizCollection(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, userid):
        try:
            user = User.objects.get(id=userid)
            if user.role == "Teacher":
                self.queryset = Quiz.objects.filter(creator=user)
                serializer = self.serializer_class(self.queryset, many=True)
                quizzes = serializer.data
                for i in range(len(quizzes)):
                    user_id = quizzes[i]['creator']
                    try:
                        user = User.objects.get(id=user_id)
                        quizzes[i]['creator_username'] = user.username
                    except ObjectDoesNotExist:
                        raise ValidationError({"message": "User do not found"})
                return Response(quizzes)
            else:
                resp = []
                self.queryset = AssignQuiz.objects.filter(user=user)
                for i in self.queryset:
                    obj = Quiz.objects.get(id=i.quiz_id)
                    serializer = self.serializer_class(obj)
                    resp.append(serializer.data)
                quizzes = resp
                for i in range(len(quizzes)):
                    user_id = quizzes[i]['creator']
                    try:
                        user = User.objects.get(id=user_id)
                        quizzes[i]['creator_username'] = user.username
                    except ObjectDoesNotExist:
                        raise ValidationError({"message": "User do not found"})
                return Response(quizzes)
        except ObjectDoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PostFeedback(GenericAPIView):
    serializer_class = FeedBackSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        if int(data['learn_new']) <= 5 and int(data['like_participating']) <= 5 and int(data['difficulty']) <= 5:
            ser = self.serializer_class(data=data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            else:
                return Response(ser.errors)
        else:
            return Response({"message": "All response must be less than or equal to 5"})


class CheckQuizAssigned(GenericAPIView):
    serializer_class = AssignQuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        try:
            quiz = Quiz.objects.get(id=data['quiz'])
            try:
                user = User.objects.get(id=data['user'])
                try:
                    assign_quiz = AssignQuiz.objects.get(quiz=quiz, user=user)
                    try:
                        quiz_response = QuizResponse.objects.get(quiz=quiz, user=user)
                        return Response({"message": "You have already attempted the test"}, status=status.HTTP_400_BAD_REQUEST)
                    except ObjectDoesNotExist:
                        return Response({"message": "Success"}, status=status.HTTP_200_OK)
                except ObjectDoesNotExist:
                    return Response({"message": "You can't attempt the quiz"}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"message": "User not found with the given id"}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response({"message": "Quiz not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

class PostUserQuizSession(APIView):
    serializer_class = UserQuizSessionSerializer
    permission_classes = [AllowAny]
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data.copy()
            quiz = Quiz.objects.get(id = data['quiz_id'])
            data['start_time '] = timezone.now()
            data['remaining_duration'] = quiz.duration
            print(data)
            ser = UserQuizSessionSerializer(data = data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors)
        
        except Exception as e:
            return Response({"msg": str(e)})


class GetUserQuizSession(GenericAPIView):
    serializer_class = UserQuizSessionSerializer
    permission_classes = [AllowAny]
    # authentication_classes = [JWTAuthentication]
    
    def get(self, request, pk):
        data = UserQuizSession.objects.get(id=pk)
        ser = UserQuizSessionSerializer(data)
        return Response(ser.data)

    def post(self, request, pk):
        try:
            sess = UserQuizSession.objects.get(id = pk)
            x = timezone.now()- sess.start_time
            y = (datetime.datetime.min +x).time()
            print(y)
            print(sess.remaining_duration)
            z = datetime.datetime.combine(datetime.date.today(),sess.remaining_duration) - datetime.datetime.combine(datetime.date.today(), y)
            print(z)
            print(type(z))
            sess.remaining_duration =  (datetime.datetime.min + z).time()
            sess.save()
            return Response({"msg":"session saved successfully"})
        except Exception as e:
            return Response({"msg": str(e)})