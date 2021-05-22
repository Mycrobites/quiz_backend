from django.views.generic.base import TemplateResponseMixin
from .serializers import *
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .permissions import *
from rest_framework.permissions import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import *
from .forms import *
from authentication.models import User
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.http import HttpResponse
import json
from django.contrib.auth.decorators import login_required
import datetime
import regex as re
from django.shortcuts import render
import pandas as pd
from csv import writer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse, redirect,Http404

import requests


# Create your views here.


class HomeView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response("Hey, Welcome to Quiz Platform!")


class QuizView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, quiz_id):
        result = {}
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.is_active(timezone.now()) or request.user.role=="Teacher":
                serializer = self.serializer_class(quiz)
                questions = quiz.question.distinct()
                quest = AddQuestion.objects.filter(quiz_id=quiz.id).order_by("createdOn")
                questions = []
                for i in quest:
                    ques_serializer = QuestionSerializer(i.question)
                    questions.append(ques_serializer.data)
                count = 0
                for i in questions:
                    i["options"] = []
                    try:
                        options = i["option"].replace("'",'"')
                        options = json.loads(options)
                    except Exception as e:
                        options = i["option"]
                    temp=[]
                    if(options is not None):
                        for i in options:
                            temp.append(options[i])
                        questions[count]["option"] = temp
                        count+=1
                result['quiz_details'] = serializer.data
                result['quiz_questions'] = questions
                return Response(result)
            else:
                return Response({"message": "This quiz is either closed now or is not opened yet"}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            raise ValidationError({"message": "Quiz not found with the given id"})


class QuizCreateView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuizEditView(GenericAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            data = request.data
            serializer = self.serializer_class(quiz, data=data,partial=True)
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
            questions = quiz.question
            marks = 0
            for i in quiz.question.all():
                if i.answer is None:
                    if res_dict[str(i.id)] == "":
                        marks += 0
                    else:
                        if i.text == res_dict[str(i.id)]:
                            marks += i.correct_marks
                        else:
                            marks -= i.negative_marks
                elif i.text == "":
                    if res_dict[str(i.id)] == "":
                        marks += 0
                    else:
                        if str(i.answer) == res_dict[str(i.id)]:
                            marks += i.correct_marks
                        else:
                            marks -= i.negative_marks
                elif i.answer == "" and i.text == "":
                    marks += 0
            quizobject = QuizResponse.objects.filter(quiz=quiz_id, user=user_id)
            quizobject.update(marks=marks)
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
            quizobj = Quiz.objects.get(id=quiz_id)
            try:
                User.objects.get(id=user_id)
                try:
                    quiz_assign = QuizResponse.objects.get(quiz=quiz_id, user=user_id)
                    serializer = self.serializer_class(quiz_assign)
                    response = serializer.data['response']
                    response = response.replace("'", '"')
                    res_dict = json.loads(response)
                    quiz = quiz_assign.quiz
                    questions = quiz.question
                    marks = 0
                    for i in quizobj.question.all():
                        if i.answer is None:
                            if res_dict[str(i.id)] == "":
                                marks += 0
                            else:
                                if i.text == res_dict[str(i.id)]:
                                    marks += i.correct_marks
                                else:
                                    marks -= i.negative_marks
                        elif i.text == "":
                            if res_dict[str(i.id)] == "":
                                marks += 0
                            else:
                                if str(i.answer) == res_dict[str(i.id)]:
                                    marks += i.correct_marks
                                else:
                                    marks -= i.negative_marks
                        elif i.answer == "" and i.text == "":
                            marks += 0
                    quizobject = QuizResponse.objects.filter(quiz=quiz_id, user=user_id)
                    quizobject.update(marks=marks)
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
                AssignQuiz.objects.get(quiz_id=data["quiz"], user=data["user"])
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
                feedback = ser.data
                feedbacks = pd.read_csv('media/feedbackResponses/output.csv', error_bad_lines=False)
                sno = len(feedbacks)
                user = User.objects.get(id=feedback['user'])
                quiz = Quiz.objects.get(id=feedback['quiz_id'])
                new_feedback = [sno, user, quiz, feedback['learn_new'],
                                feedback['like_participating'], feedback['difficulty'],
                                feedback['participate_again'], feedback['time_sufficient'],
                                feedback['attend_webinar'], feedback['language_english'],
                                feedback['mini_course'], feedback['next_contest'],
                                feedback['suggestions'], feedback['username']]
                with open('media/feedbackResponses/output.csv', 'a') as f_object:
                    writer_object = writer(f_object)
                    writer_object.writerow(new_feedback)
                    f_object.close()
                return Response(feedback)
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
            if(quiz.is_active(timezone.now())):
                try:
                    user = User.objects.get(id=data['user'])
                    try:
                        assign_quiz = AssignQuiz.objects.get(quiz=quiz, user=user)
                        try:
                            quiz_response = QuizResponse.objects.get(quiz=quiz, user=user)
                            return Response({"message": "You have already attempted the test"},
                                            status=status.HTTP_400_BAD_REQUEST)
                        except ObjectDoesNotExist:
                            return Response({"message": "Success"}, status=status.HTTP_200_OK)
                    except ObjectDoesNotExist:
                        return Response({"message": "You can't attempt the quiz"}, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({"message": "User not found with the given id"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "This quiz is either not open yet or is now closed"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Quiz not found with the given id"}, status=status.HTTP_404_NOT_FOUND)


class PostUserQuizSession(APIView):
    serializer_class = UserQuizSessionSerializer
    permission_classes = [AllowAny]

    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data.copy()
            quiz = Quiz.objects.get(id=data['quiz_id'])
            data['start_time '] = timezone.now()
            data['remaining_duration'] = quiz.duration
            ser = UserQuizSessionSerializer(data=data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data)
            return Response(ser.errors)

        except Exception as e:
            return Response({"msg": str(e)})


class GetUserQuizSession(GenericAPIView):
    serializer_class = UserQuizSessionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        sess = UserQuizSession.objects.get(id=pk)
        x = timezone.now() - sess.start_time
        y = (datetime.datetime.min + x).time()
        z = datetime.datetime.combine(datetime.date.today(), sess.remaining_duration) - datetime.datetime.combine(
            datetime.date.today(), y)
        sess.remaining_duration = (datetime.datetime.min + z).time()
        sess.save()
        ser = UserQuizSessionSerializer(sess)
        return Response(ser.data)


def filterscore(request):
    if request.method == "POST":
        error = ""
        username = request.POST['user']
        quizid = request.POST['quizid']
        subject = request.POST['subject']
        topic = request.POST['topic']
        subtopic = request.POST['subtopic']
        difficulty = request.POST['difficulty']
        skill = request.POST['skill']
        try:
            user = User.objects.get(username=username)
        except:
            error = "user does not exist"
            return render(request, "filterscore.html", {"error": error})
        try:
            q = QuizResponse.objects.get(user=user.id, quiz=quizid)
        except:
            error = "no matching username and quizid found"
            return render(request, "filterscore.html", {"error": error})
        response = q.response.replace("'", '"')
        res_dict = json.loads(response)
        score = 0

        dicti = {"subject": 1, "topic": 1, "subtopic": 1, "difficulty": 1, "skill": 1}
        if subject == "None":
            dicti["subject"] = 0
        if topic == "None":
            dicti["topic"] = 0
        if subtopic == "None":
            dicti["subtopic"] = 0
        if difficulty == "None":
            dicti["difficulty"] = 0
        if skill == "None":
            dicti["skill"] = 0

        tags = []
        i = 0
        for key, value in dicti.items():
            i = i + 1
            if value == 1:
                tags.append(i)

        temp = 1

        if subject == "None" and topic == "None" and subtopic == "None" and difficulty == "None" and skill == "None":
            score = q.marks
        else:
            for key, value in res_dict.items():
                if value:
                    ques = Question.objects.get(id=key)
                    temp = 1
                    for tag in tags:
                        if tag == 1:
                            if subject == ques.subject_tag:
                                temp = temp * 1
                            else:
                                temp = temp * 0
                        elif tag == 2:
                            if topic == ques.topic_tag:
                                temp = temp * 1
                            else:
                                temp = temp * 0
                        elif tag == 3:
                            if subtopic == ques.subtopic_tag:
                                temp = temp * 1
                            else:
                                temp = temp * 0
                        elif tag == 4:
                            if difficulty == ques.dificulty_tag:
                                temp = temp * 1
                            else:
                                temp = temp * 0
                        else:
                            if skill == ques.skill:
                                temp = temp * 1
                            else:
                                temp = temp * 0

                    if temp == 1:
                        if str(value) == str(ques.answer) or str(value) == str(ques.text):
                            score += ques.correct_marks
                        else:
                            score -= ques.negative_marks
        return render(request, "filterscore.html", {"score": score, "error": error})
    else:
        return render(request, "filterscore.html")


def result(request):
    return render(request, "result.html")


def resultanalysis(request):
    if request.method == "POST":
        error = ""
        username = request.POST['user']
        quizid = request.POST['quizid']
        try:
            user = User.objects.get(username=username)
        except:
            error = "user does not exist"
            return render(request, "result.html", {"error": error})
        try:
            q = QuizResponse.objects.get(user=user.id, quiz=quizid)
        except:
            error = "no matching username and quizid found"
            return render(request, "result.html", {"error": error})
        response = q.response.replace("'", '"')
        res_dict = json.loads(response)

        details = {"total": {}, "easy": {}, "med": {}, "hard": {}, "algebra": {}, "calculus": {}, "combinatorics": {},
                   "geometry": {}, "logicalThinking": {}, "numberTheory": {}}

        details["total"]["total questions"] = len(res_dict)

        posscore = negscore = easyTot = easyPos = easyNeg = medTot = medPos = medNeg = hardTot = hardPos = hardNeg = 0
        algebraTot = algebraPos = algebraNeg = calculusTot = calculusPos = calculusNeg = combinatoricsTot = combinatoricsPos = combinatoricsNeg = 0
        geometryTot = geometryPos = geometryNeg = logicalThinkingTot = logicalThinkingPos = logicalThinkingNeg = numberTheoryTot = numberTheoryPos = numberTheoryNeg = 0

        for key, value in res_dict.items():
            ques = Question.objects.get(id=key)
            if ques.dificulty_tag == "Easy":
                easyTot += 1
            elif ques.dificulty_tag == "Medium":
                medTot += 1
            elif ques.dificulty_tag == "Hard":
                hardTot += 1

            if ques.topic_tag == "Algebra":
                algebraTot += 1
            elif ques.topic_tag == "Calculus":
                calculusTot += 1
            elif ques.topic_tag == "Combinatorics":
                combinatoricsTot += 1
            elif ques.topic_tag == "Geometry":
                geometryTot += 1
            elif ques.topic_tag == "Logical Thinking":
                logicalThinkingTot += 1
            else:
                numberTheoryTot += 1

            details["easy"]["total questions"] = easyTot
            details["med"]["total questions"] = medTot
            details["hard"]["total questions"] = hardTot
            details["algebra"]["total questions"] = algebraTot
            details["calculus"]["total questions"] = calculusTot
            details["combinatorics"]["total questions"] = combinatoricsTot
            details["geometry"]["total questions"] = geometryTot
            details["logicalThinking"]["total questions"] = logicalThinkingTot
            details["numberTheory"]["total questions"] = numberTheoryTot

            if value:
                if str(value) == str(ques.answer) or str(value) == str(ques.text):
                    posscore += 1
                    if ques.dificulty_tag == "Easy":
                        easyPos += 1
                    elif ques.dificulty_tag == "Medium":
                        medPos += 1
                    elif ques.dificulty_tag == "Hard":
                        hardPos += 1

                    if ques.topic_tag == "Algebra":
                        algebraPos += 1
                    elif ques.topic_tag == "Calculus":
                        calculusPos += 1
                    elif ques.topic_tag == "Combinatorics":
                        combinatoricsPos += 1
                    elif ques.topic_tag == "Geometry":
                        geometryPos += 1
                    elif ques.topic_tag == "Logical Thinking":
                        logicalThinkingPos += 1
                    else:
                        numberTheoryPos += 1
                else:
                    negscore += 1
                    if ques.dificulty_tag == "Easy":
                        easyNeg += 1
                    elif ques.dificulty_tag == "Medium":
                        medNeg += 1
                    elif ques.dificulty_tag == "Hard":
                        hardNeg += 1

                    if ques.topic_tag == "Algebra":
                        algebraNeg += 1
                    elif ques.topic_tag == "Calculus":
                        calculusNeg += 1
                    elif ques.topic_tag == "Combinatorics":
                        combinatoricsNeg += 1
                    elif ques.topic_tag == "Geometry":
                        geometryNeg += 1
                    elif ques.topic_tag == "Logical Thinking":
                        logicalThinkingNeg += 1
                    else:
                        numberTheoryNeg += 1

        details["total"]["correct questions"] = posscore
        details["total"]["Incorrect questions"] = negscore

        details["easy"]["correct questions"] = easyPos
        details["easy"]["Incorrect questions"] = easyNeg
        details["med"]["correct questions"] = medPos
        details["med"]["Incorrect questions"] = medNeg
        details["hard"]["correct questions"] = hardPos
        details["hard"]["Incorrect questions"] = hardNeg

        details["algebra"]["correct questions"] = algebraPos
        details["algebra"]["Incorrect questions"] = algebraNeg
        details["calculus"]["correct questions"] = calculusPos
        details["calculus"]["Incorrect questions"] = calculusNeg
        details["combinatorics"]["correct questions"] = combinatoricsPos
        details["combinatorics"]["Incorrect questions"] = combinatoricsNeg
        details["geometry"]["correct questions"] = geometryPos
        details["geometry"]["Incorrect questions"] = geometryNeg
        details["logicalThinking"]["correct questions"] = logicalThinkingPos
        details["logicalThinking"]["Incorrect questions"] = logicalThinkingNeg
        details["numberTheory"]["correct questions"] = numberTheoryPos
        details["numberTheory"]["Incorrect questions"] = numberTheoryNeg

        return render(request, "resultanalysis.html", {"username": username, "quizid": quizid, "details": details})


class GetResult(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, username,quizid):
        result = {}
        try:
            user = User.objects.get(username=username)
        except:
            error = "user does not exist"
            return Response({"message": error})
        try:
            quizes = QuizResponse.objects.get(quiz_id=quizid,user=user.id)
        except:
            error = "The user has attempted this quiz"
            return Response({"message": error})
        quizes = QuizResponse.objects.filter(quiz_id=quizid,user=user.id)
        arr = []
        for q in quizes:
            quizobj = Quiz.objects.get(title=q.quiz)
            totalquestion = 0
            attemptedquestion = 0
            nonattempted = 0
            correctquestion = 0
            wrongquestion = 0
            totalmarks = 0
            dic = {}
            quesdic = {}
            response = q.response.replace("'", '"')
            res_dict = json.loads(response)
            for ques in res_dict:
                totalquestion += 1
                obj = Question.objects.get(id=ques)
                if obj.answer is None:
                    quesdic["Question " + str(totalquestion)] = {"question":obj.question,"correct answer": obj.text,
                                                                 "your answer": res_dict[ques]}
                else:
                    if(type(obj.option) is str):
                        temp = obj.option.replace("'",'"')
                        temp = json.loads(temp)
                    else:
                        temp = obj.option
                    if res_dict[ques] != "":
                        try:
                            quesdic["Question " + str(totalquestion)] = {"question":obj.question,"correct answer": temp[str(obj.answer)],
                                                                     "your answer":temp[str(res_dict[ques])]}
                        except:
                            quesdic["Question " + str(totalquestion)] = {"question":obj.question,"correct answer": "option " + str(obj.answer),
                                                                     "your answer": "option " + str(res_dict[ques])}
                    else:
                        try:
                            quesdic["Question " + str(totalquestion)] = {"question":obj.question,"correct answer":  temp[str(obj.answer)],
                                                                     "your answer": ""}
                        except:
                            quesdic["Question " + str(totalquestion)] = {"question":obj.question,"correct answer": "option " + str(obj.answer),
                                                                     "your answer": ""}
                if res_dict[ques] != "":
                    attemptedquestion += 1
                    if ((obj.answer is not None and str(obj.answer) == str(res_dict[ques])) or str(obj.text) == str(
                            res_dict[ques])):
                        correctquestion += 1
                        totalmarks += int(obj.correct_marks)
                        flag = "True"
                    else:
                        wrongquestion += 1
                        totalmarks -= int(obj.negative_marks)
                        flag = "False"
                else:
                    nonattempted += 1
                    flag = "Not attempted"
                subjecttag = obj.subject_tag
                if subjecttag is not None and subjecttag.strip() != "":
                    try:
                        dic["subject: " + subjecttag]["total_questions"] += 1
                        if flag == "True":
                            dic["subject: " + subjecttag]["correct_questions"] += 1
                        else:
                            dic["subject: " + subjecttag]["incorrect_or_not_attempted"] += 1
                    except:
                        dic["subject: " + subjecttag] = {}
                        dic["subject: " + subjecttag]["total_questions"] = 1
                        if flag == "True":
                            dic["subject: " + subjecttag]["correct_questions"] = 1
                            dic["subject: " + subjecttag]["incorrect_or_not_attempted"] = 0
                        else:
                            dic["subject: " + subjecttag]["incorrect_or_not_attempted"] = 1
                            dic["subject: " + subjecttag]["correct_questions"] = 0
                topictag = obj.subtopic_tag
                if topictag is not None and topictag.strip() != "":
                    try:
                        dic["topic: " + topictag]["total_questions"] += 1
                        if flag == "True":
                            dic["topic: " + topictag]["correct_questions"] += 1
                        else:
                            dic["topic: " + topictag]["incorrect_or_not_attempted"] += 1
                    except:
                        dic["topic: " + topictag] = {}
                        dic["topic: " + topictag]["total_questions"] = 1
                        if flag == "True":
                            dic["topic: " + topictag]["correct_questions"] = 1
                            dic["topic: " + topictag]["incorrect_or_not_attempted"] = 0
                        else:
                            dic["topic: " + topictag]["incorrect_or_not_attempted"] = 1
                            dic["topic: " + topictag]["correct_questions"] = 0
                subtopictag = obj.topic_tag
                if subtopictag is not None and subtopictag.strip() != "":
                    try:
                        dic["subtopic: " + subtopictag]["total_questions"] += 1
                        if flag == "True":
                            dic["subtopic: " + subtopictag]["correct_questions"] += 1
                        else:
                            dic["subtopic: " + subtopictag]["incorrect_or_not_attempted"] += 1
                    except:
                        dic["subtopic: " + subtopictag] = {}
                        dic["subtopic: " + subtopictag]["total_questions"] = 1
                        if flag == "True":
                            dic["subtopic: " + subtopictag]["correct_questions"] = 1
                            dic["subtopic: " + subtopictag]["incorrect_or_not_attempted"] = 0
                        else:
                            dic["subtopic: " + subtopictag]["incorrect_or_not_attempted"] = 1
                            dic["subtopic: " + subtopictag]["correct_questions"] = 0
                skilltag = obj.skill
                if skilltag is not None and skilltag.strip() != "":
                    try:
                        dic["skill: " + skilltag]["total_questions"] += 1
                        if flag == "True":
                            dic["skill: " + skilltag]["correct_questions"] += 1
                        else:
                            dic["skill: " + skilltag]["incorrect_or_not_attempted"] += 1
                    except:
                        dic["skill: " + skilltag] = {}
                        dic["skill: " + skilltag]["total_questions"] = 1
                        if flag == "True":
                            dic["skill: " + skilltag]["correct_questions"] = 1
                            dic["skill: " + skilltag]["incorrect_or_not_attempted"] = 0
                        else:
                            dic["skill: " + skilltag]["incorrect_or_not_attempted"] = 1
                            dic["skill: " + skilltag]["correct_questions"] = 0
                dificultytag = obj.dificulty_tag
                if  dificultytag is not None and dificultytag.strip() != "":
                    try:
                        dic["dificulty: " + dificultytag]["total_questions"] += 1
                        if flag == "True":
                            dic["dificulty: " + dificultytag]["correct_questions"] += 1
                        else:
                            dic["dificulty: " + dificultytag]["incorrect_or_not_attempted"] += 1
                    except:
                        dic["dificulty: " + dificultytag] = {}
                        dic["dificulty: " + dificultytag]["total_questions"] = 1
                        if flag == "True":
                            dic["dificulty: " + dificultytag]["correct_questions"] = 1
                            dic["dificulty: " + dificultytag]["incorrect_or_not_attempted"] = 0
                        else:
                            dic["dificulty: " + dificultytag]["incorrect_or_not_attempted"] = 1
                            dic["dificulty: " + dificultytag]["correct_questions"] = 0
            result = {"Quiz Name": quizobj.title + " by " + str(quizobj.creator), "totalquestion": totalquestion,
                      "correctquestion": correctquestion, "incorrectquestion": wrongquestion,
                      "attempted": attemptedquestion, "not_attempted": nonattempted, "marks_obtained": totalmarks,
                      "responses": quesdic, "analysis": dic}
            arr.append(result)
        return Response({"data": result})


class CreateExcelForScore(APIView):
    permission_classes = [AllowAny]

    def get(self, request,quizid):
        users = QuizResponse.objects.filter(quiz_id=quizid).values_list('user', flat=True)

        f_object = open('media/result_response/output_result.csv', 'w')
        writer_object = writer(f_object)
        writer_object.writerow(
            ['S No', 'User', 'Quiz Name', 'Total Question', 'Correct', 'Incorrect', 'Attempted', 'Not Attempted',
             'Marks'])

        f_object_question = open('media/result_response/output_result_question.csv', 'w')
        writer_object_question = writer(f_object_question)
        writer_object_question.writerow(['S No', 'User', 'Question No',"Question", 'Correct Answer', 'User Answer'])

        f_object_tag = open('media/result_response/output_result_tag.csv', 'w')
        writer_object_tag = writer(f_object_tag)
        writer_object_tag.writerow(
            ['S No', 'User', 'Analysis On', 'Total Question', 'Correct', 'Incorrect Or Not Attempted'])

        sno = 1
        for user in users:
            try:
                user = User.objects.get(id=user).username
                data = requests.get(f'https://api.progressiveminds.in/api/getresult/{user}/{quizid}').json()['data']
                ## basic analysis
                new_result = [sno, user, data['Quiz Name'], data['totalquestion'], data['correctquestion'],
                              data['incorrectquestion'],
                              data['attempted'], data['not_attempted'], data['marks_obtained']]
                writer_object.writerow(new_result)

                for quest, resp in data['responses'].items():
                    new_result_question = [sno, user, quest,resp["question"], resp['correct answer'], resp['your answer']]
                    writer_object_question.writerow(new_result_question)

                for tag, resp in data['analysis'].items():
                    new_result_tag = [sno, user, tag, resp['total_questions'], resp['correct_questions'],
                                      resp['incorrect_or_not_attempted']]
                    writer_object_tag.writerow(new_result_tag)

                sno += 1


            except Exception as e:
                print(e)
                print('kx to gadbad hai')

        f_object.close()
        f_object_question.close()
        f_object_tag.close()

        df1 = pd.read_csv('media/result_response/output_result_question.csv')
        df2 = pd.read_csv('media/result_response/output_result_tag.csv')
        df3 = pd.read_csv('media/result_response/output_result.csv')

        with pd.ExcelWriter('media/result_response/Result.xlsx') as Main:
            df3.to_excel(Main, sheet_name='Basic_Analysis', index=False)
            df1.to_excel(Main, sheet_name='Question_Analysis', index=False)
            df2.to_excel(Main, sheet_name='Tag_Analysis', index=False)
        print('************************ bas khatam ***************************')
        with open("media/result_response/Result.xlsx", "rb") as excel:
            content = excel.read()
        response = HttpResponse(content=content, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Result.xlsx"'
        return response


class DeleteQuestionFromQuiz(GenericAPIView):

    serializer_class = QuizResponseSerializer
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, quiz_id, question_id):
        try:

            obj = AddQuestion.objects.get(quiz_id=quiz_id,question_id=question_id)
            obj.delete()
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_questions = quiz.question
            quiz_questions.remove(question_id)
        except Exception as e:
            print(e)
            return Response({"message": "Cannot delete the question"})
        # Quiz.objects.filter(id=quiz_id).update(questions=quiz_questions)
        return Response({"message": "Question removed from the quiz successfully"})


class AddQuestionToQuiz(APIView):

    serializer_class = QuizResponseSerializer
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            quiz = Quiz.objects.get(id=request.data['quiz_id'])
            quest_ids = request.data['quest_id']

            for q in quest_ids:
                try:
                    quest = Question.objects.get(id=str(q))
                    quiz.question.add(quest)
                    obj = AddQuestion.objects.create(quiz_id=quiz.id,question_id=quest.id)
                    obj.save()
                    quiz.save()
                except Exception:
                    return Response({"message": f"{q}, not valid"}, status=400)

            return Response({"message": "added successfully"}, status=200)
        except Exception:
            return Response({"message": "something went wrong"}, status=400)

class QuestionBankListView(GenericAPIView):
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]
    serializer_class = QuestionSerializer

    def get(self,request,quizid):
        given_quiz=Quiz.objects.get(id=quizid)
        qu=AddQuestion.objects.filter(quiz_id=quizid)
        already=[]
        for i in qu:
            already.append(str(i.question.id))        
        self.queryset = Question.objects.all().exclude(id__in=already)
        serializer = self.serializer_class(self.queryset, many=True)
        tags = {"subject": "", "dificulty": ["Easy", "Medium", "Hard"], "skill": ""}
        subjecttags = Question.objects.values_list("subject_tag").distinct()
        skill = Question.objects.values_list("skill").distinct()
        tags["skill"]=[i[0].strip() for i in skill if i is not None ]
        tags["subject"] = []
        for i in subjecttags:
            if (i[0] and i[0].strip() != ""):
                temp = {}
                subject = i[0]
                temp['name']=subject
                temp["topics"] = []
                temp1={}
                topictags = Question.objects.filter(subject_tag=subject).values_list("topic_tag").distinct()
                for j in topictags:
                    if (j[0] and j[0].strip() != ""):
                        topic = j[0]
                        temp1["name"]=j[0]
                        subtopicstags = Question.objects.filter(subject_tag=subject, topic_tag=topic).values_list(
                            "subtopic_tag").distinct()
                        subtopiclist = [k[0] for k in subtopicstags if k[0].strip() != ""]
                        temp1["subTopics"] = subtopiclist
                    temp["topics"].append(temp1)

                tags["subject"].append(temp)
        count = 0
        for i in serializer.data:
            i["options"] = []
            try:
                options = i["option"].replace("'",'"')
                options = json.loads(options)
            except Exception as e:
                options = i["option"]
            temp=[]
            if(options is not None):
                for i in options:
                    temp.append(options[i])
                serializer.data[count]["option"] = temp
                count+=1
        response = {"questions": serializer.data, "tags": tags}
        return Response(response)





################################ functions for question bank
##################################
##################################




@login_required
def getBank(request):
    questions = Question.objects.all() 
    try:
        subject = request.GET["subject_tag"]
        questions = Question.objects.filter(subject_tag=subject)
    except:       
        pass
    try:
        subject = request.GET["topic_tag"]
        questions = Question.objects.filter(topic_tag=subject)
    except:       
        pass
    try:
        subject = request.GET["subtopic_tag"]
        questions = Question.objects.filter(subtopic_tag=subject)
    except:       
        pass
    try:
        subject = request.GET["dificulty"]
        questions = Question.objects.filter(dificulty_tag=subject)
    except:       
        pass
    try:
        subject = request.GET["skill"]
        questions = Question.objects.filter(skill=subject)
    except:       
        pass
    subjecttags = Question.objects.values_list("subject_tag").distinct()
    dificulty = [("Easy"),("Medium"),("Hard")]
    skill =Question.objects.values_list("skill").distinct()
    subtopicstags = Question.objects.all().values_list("subtopic_tag").distinct()
    topictags = Question.objects.all().values_list("topic_tag").distinct()
    return render(request,"questions.html",{"questions":questions,"subjects":subjecttags,"topics":topictags,"subtopics":subtopicstags,"dificulty":dificulty,"skill":skill})

@login_required
def deleteQuestions(request):
    queryset = json.loads(request.POST["objects"])
    for i in queryset:
        Question.objects.get(id=i).delete()

    return HttpResponse("done")

def bank(request):
    if(request.method=="POST"):
        question = request.POST["question"]
        try:
            answer = request.POST["answer"]
            if(answer.strip()==""):
                answer = None
        except:
            answer = None
        try:
            text = request.POST["text"]
        except:
            text = None
        correct_marks = request.POST["correct_marks"]
        negative_marks = request.POST["negative_marks"]
        totaloptions = request.POST["totaloption"]
        try:
            dificulty_tag = request.POST["dificulty_tag"]
        except:
            dificulty_tag = "Easy"
        try:
            skill = request.POST["skill"]
        except:
            skill = None
        try:
            subject_tag = request.POST["subject_tag"]
        except:
            subject_tag = None
        try:
            topic_tag = request.POST["topic_tag"]
        except:
            topic_tag = None
        try:
            subtopic_tag = request.POST["subtopic_tag"]
        except:
            subtopic_tag = None
        count = 1
        option = {}
        for i in range(int(totaloptions)+1):
            try:
                temp = request.POST["option"+str(i)]
                if(temp.strip()!=""):
                    option[count] = temp
                    count+=1
            except:
                pass
        try:
           id =  request.POST["id"]
           questionobj = Question.objects.get(id=id)
           questionobj.answer = answer
           questionobj.text = text
           questionobj.subject_tag = subject_tag
           questionobj.topic_tag = topic_tag
           questionobj.subtopic_tag = subtopic_tag
           questionobj.dificulty_tag = dificulty_tag
           questionobj.skill = skill
           questionobj.question = question
           questionobj.option = option
           questionobj.correct_marks = correct_marks
           questionobj.negative_marks = negative_marks
           questionobj.save()
           return redirect("/questionbank")
        except:
            pass
        obj = Question.objects.create(question=question,option=option,answer=answer,correct_marks=correct_marks,negative_marks=negative_marks,text=text,subject_tag=subject_tag,topic_tag=topic_tag,subtopic_tag=subtopic_tag,dificulty_tag=dificulty_tag,skill=skill)
        return redirect("/questionbank")
    form = QuestionForm
    subjecttags = Question.objects.values_list("subject_tag").distinct()
    dificulty = [("Easy"),("Medium"),("Hard")]
    skill =Question.objects.values_list("skill").distinct()
    subtopicstags = Question.objects.all().values_list("subtopic_tag").distinct()
    topictags = Question.objects.all().values_list("topic_tag").distinct()
    return render(request,"Questionbank.html",{"form":form,"subjects":subjecttags,"topics":topictags,"subtopics":subtopicstags,"dificulty":dificulty,"skill":skill})


def editBank(request,qid):
    try:
        question = Question.objects.get(id=qid)
    except:
        raise Http404
    try:
        optionlist = question.option.values()
    except:
        optionlist = []
    form = QuestionForm(instance=question)
    subjecttags = Question.objects.values_list("subject_tag").distinct()
    dificulty = [("Easy"),("Medium"),("Hard")]
    skill =Question.objects.values_list("skill").distinct()
    subtopicstags = Question.objects.all().values_list("subtopic_tag").distinct()
    topictags = Question.objects.all().values_list("topic_tag").distinct()
    if(len(optionlist)!=0):
        return render(request,"Questionbank.html",{"options":optionlist,"question":question,"form":form,"subjects":subjecttags,"topics":topictags,"subtopics":subtopicstags,"dificulty":dificulty,"skill":skill})
    else:
        return render(request,"Questionbank.html",{"question":question,"form":form,"subjects":subjecttags,"topics":topictags,"subtopics":subtopicstags,"dificulty":dificulty,"skill":skill})


@login_required
def tagquestion(request):
    questions = Question.objects.all()
    subjecttags = Question.objects.values_list("subject_tag").distinct()
    dificulty = [("Easy"),("Medium"),("Hard")]
    skill =Question.objects.values_list("skill").distinct()
    try:
        subject = request.GET["subjecttag"]
        topic = request.GET["topictag"]
        subtopicstags = Question.objects.filter(subject_tag=subject,topic_tag=topic).values_list("subtopic_tag").distinct()
        return render(request,"tagquestion.html",{"questions":questions,"subjects":subject,"topics":topic,"subtopics":subtopicstags,"dificulty":dificulty,"skill":skill})
    except:
        pass
    try:
        subject = request.GET["subjecttag"]
        topictags = Question.objects.filter(subject_tag=subject).values_list("topic_tag").distinct()
        return render(request,"tagquestion.html",{"questions":questions,"subjects":subject,"topics":topictags,"dificulty":dificulty,"skill":skill})
    except:
        pass
    return render(request,"tagquestion.html",{"questions":questions,"subjects":subjecttags,"dificulty":dificulty,"skill":skill})


@login_required
def Addtags(request):
    queryset = json.loads(request.POST["queryset"])
    subject = request.POST["subject"]
    try:
        topic = request.POST["topic"]
    except:
        topic = ""
    try:
        subtopic = request.POST["subtopic"]
    except:
        subtopic = ""
    dificulty = request.POST["dificulty"]
    skill = request.POST["skill"]

    for i in queryset:
        obj = Question.objects.get(id=i)
        obj.subject_tag = subject
        obj.topic_tag = topic
        obj.subtopic_tag = subtopic
        obj.dificulty_tag = dificulty
        obj.skill = skill
        obj.save()
    return HttpResponse("done")



@csrf_exempt
def uploadimage(request):
    # name = request.FILES["upload"].name
    obj = upload_image.objects.create(file=request.FILES["upload"])
    obj.save()
    path = str(obj.file)
    url = "https://lab.progressiveminds.in/media/" + path
    return HttpResponse(json.dumps({"url": url, "uploaded": True}))

def lmsBank(request):
    try:
        subject = request.GET["subject_tag"]
        subject_filter=subject
    except:       
        subject_filter=""
    try:
        subject = request.GET["topic_tag"]
        topic_filter = subject
    except:       
        topic_filter=""
    try:
        subject = request.GET["subtopic_tag"]
        subtopic_filter = subject
    except:       
        subtopic_filter=""
    try:
        subject = request.GET["dificulty"]
        dificulty_filter = subject
    except:       
        dificulty_filter=""
    try:
        subject = request.GET["skill"]
        skill_filter = subject
    except:       
        skill_filter=""
    questions = requests.get("https://lab.progressiveminds.in/teacher/getQuestionsFromQB")
    questions = questions.json()
    skill = questions["tags"]["skill"]
    dificulty = [("Easy"),("Medium"),("Hard")] 
    subject = []
    topic = []
    subtopic = []
    for i in questions["tags"]["subject"]:
        subject.append(i["name"])
        for j in i["topics"]:
            topic.append(j["name"])
            for k in j["subTopics"]:
                    subtopic.append(k)
    return render(request,"pmbank.html",{"questions":questions["questions"],"subjects":subject,"topics":topic,"subtopics":subtopic,"dificulty":dificulty,"skill":skill,"subject_filter":subject_filter,"topic_filter":topic_filter,"subtopic_filter":subtopic_filter,"dificulty_filter":dificulty_filter,"skill_filter":skill_filter})


def importQuestion(request):
    if(request.method=="POST"):
        questionids = json.loads(request.POST["questions"])
        for i in questionids:
                i = i[1:-1]
                i = i.split(",")
                if(len(i)==11 and i[-1]=="[]"):
                    options = ""
                else:
                    options = {}
                    count = 10
                    for j in range(len(i)-10):
                        temp = i[count].lstrip("[").rstrip("]")
                        options[str(j+1)] = temp.strip(" ' ")
                        count+=1
                if(i[9]!='None'):
                    obj = Question.objects.create(option=str(options),text=i[8],question=i[0],answer=i[9],correct_marks=int(i[1]),negative_marks=int(i[2]),subject_tag=i[3],topic_tag=i[4],subtopic_tag=i[5],dificulty_tag=i[6],skill=i[7])
                    obj.save()
                else:
                    obj = Question.objects.create(option=str(options),text=i[8],question=i[0],correct_marks=int(i[1]),negative_marks=int(i[2]),subject_tag=i[3],topic_tag=i[4],subtopic_tag=i[5],dificulty_tag=i[6],skill=i[7])
                    obj.save()
    return HttpResponse("nonne")
