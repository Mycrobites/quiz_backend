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
import datetime
import regex as re
from django.shortcuts import render


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
                    string = questions[i]["question"]
                    for j in range(len(string)):
                        if string[j] == "s" and string[j + 1] == "r" and string[j + 2] == "c" and string[j + 3] == "=":
                            string = string[:j + 5] + "http://18.222.104.46" + string[j + 5:]
                    questions[i]["question"] = string
                    try:
                        matched_strings = re.findall(r'\"(.+?)\"', questions[i]['option'])
                        options = questions[i]['option'].replace("'", '"')
                        for ms in matched_strings:
                            new_str = ms.replace("'", '"')
                            options = options.replace(new_str, ms)
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
            quiz = Quiz.objects.get(id=data['quiz_id'])
            data['start_time '] = timezone.now()
            data['remaining_duration'] = quiz.duration
            print(data)
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
        sess = UserQuizSession.objects.get(id = pk)
        x = timezone.now()- sess.start_time
        y = (datetime.datetime.min +x).time()
        z = datetime.datetime.combine(datetime.date.today(),sess.remaining_duration) - datetime.datetime.combine(datetime.date.today(), y)
        sess.remaining_duration =  (datetime.datetime.min + z).time()
        sess.save()
        ser = UserQuizSessionSerializer(sess)
        return Response(ser.data)

def filterscore(request):
    if request.method=="POST":
        error=""
        username=request.POST['user']
        quizid=request.POST['quizid']
        subject=request.POST['subject']
        topic=request.POST['topic']
        subtopic=request.POST['subtopic']
        difficulty=request.POST['difficulty']
        skill=request.POST['skill']
        try:
            user=User.objects.get(username=username)
        except:
            error="user does not exist"
            return render(request,"filterscore.html",{"error":error})
        try:
            q=QuizResponse.objects.get(user=user.id,quiz=quizid)
        except:
            error="no matching username and quizid found"
            return render(request,"filterscore.html",{"error":error})
        response = q.response.replace("'", '"')
        res_dict = json.loads(response)
        score=0

        dicti = {"subject":1,"topic":1,"subtopic":1,"difficulty":1,"skill":1}
        if(subject=="None"):
            dicti["subject"]= 0
        if(topic=="None"):
            dicti["topic"]= 0
        if(subtopic=="None"):
            dicti["subtopic"]= 0
        if(difficulty=="None"):
            dicti["difficulty"]= 0
        if(skill=="None"):
            dicti["skill"]= 0

        tags=[]
        i=0
        for key,value in dicti.items():
            i=i+1
            if(value==1):
                tags.append(i)
               
        temp=1

        if(subject=="None" and topic=="None" and subtopic=="None" and difficulty=="None" and skill=="None"):
            score=q.marks
        else:
            for key,value in res_dict.items():
                if(value):
                    ques=Question.objects.get(id=key)
                    temp=1
                    for tag in tags:
                        if(tag==1):
                            if(subject==ques.subject_tag):
                                temp= temp * 1
                            else:
                                temp=temp*0
                        elif(tag==2):
                            if(topic==ques.topic_tag):
                                temp= temp * 1
                            else:
                                temp=temp*0
                        elif(tag==3):
                            if(subtopic==ques.subtopic_tag):
                                temp= temp * 1
                            else:
                                temp=temp*0
                        elif(tag==4):
                            if(difficulty==ques.dificulty_tag):
                                temp= temp * 1
                            else:
                                temp=temp*0
                        else:
                            if(skill==ques.skill):
                                temp= temp * 1
                            else:
                                temp=temp*0
                    
                    if(temp==1):
                        if str(value)==str(ques.answer):
                            print("sahi",value,ques.answer)
                            score+=ques.correct_marks
                        else:
                            print("galat",value,ques.answer)
                            score-=ques.negative_marks
        return render(request,"filterscore.html",{"score":score,"error":error})
    else:
        return render(request,"filterscore.html")


def result(request):
    return render(request,"result.html")

def resultanalysis(request):
    if request.method=="POST":
        error=""
        username=request.POST['user']
        quizid=request.POST['quizid']
        try:
            user=User.objects.get(username=username)
        except:
            error="user does not exist"
            return render(request,"result.html",{"error":error})
        try:
            q=QuizResponse.objects.get(user=user.id,quiz=quizid)
        except:
            error="no matching username and quizid found"
            return render(request,"result.html",{"error":error})
        response = q.response.replace("'", '"')
        res_dict = json.loads(response)
        details={}
        easy={}
        med={}
        hard={}
        details["Total Marks Obtained"]=q.marks
        details["Total Questions"]=len(res_dict)
        posscore=negscore=attempt=easyTot=easyAttempt=easyPos=easyNeg=medTot=medAttempt=medPos=medNeg=hardTot=hardAttempt=hardPos=hardNeg=0
        for key,value in res_dict.items():
            ques=Question.objects.get(id=key)
            if(ques.dificulty_tag=="Easy"):
                easyTot+=1
            elif(ques.dificulty_tag=="Medium"):
                medTot+=1
            elif(ques.dificulty_tag=="Hard"):
                hardTot+=1
            easy["Total Questions"]=easyTot
            med["Total Questions"]=medTot
            hard["Total Questions"]=hardTot
            if(value):
                attempt+=1
                if(ques.dificulty_tag=="Easy"):
                    easyAttempt+=1
                elif(ques.dificulty_tag=="Medium"):
                    medAttempt+=1
                elif(ques.dificulty_tag=="Hard"):
                    hardAttempt+=1
                if str(value)==str(ques.answer):
                    posscore+=ques.correct_marks
                    if(ques.dificulty_tag=="Easy"):
                        easyPos+=ques.correct_marks
                    elif(ques.dificulty_tag=="Medium"):
                        medPos+=ques.correct_marks
                    elif(ques.dificulty_tag=="Hard"):
                        hardPos+=ques.correct_marks
                else:
                    negscore-=ques.negative_marks
                    if(ques.dificulty_tag=="Easy"):
                        easyNeg-=ques.negative_marks
                    elif(ques.dificulty_tag=="Medium"):
                        medNeg-=ques.negative_marks
                    elif(ques.dificulty_tag=="Hard"):
                        hardNeg-=ques.negative_marks
        details["Attempted"]=attempt
        details["Not Attempted"]=details["Total Questions"]-attempt
        details["Positive Score"]=posscore
        details["Negative Score"]=negscore
        easy["Attempted"]=easyAttempt
        med["Attempted"]=medAttempt
        hard["Attempted"]=hardAttempt
        easy["Not Attempted"]=easy["Total Questions"]-easyAttempt
        med["Not Attempted"]=med["Total Questions"]-medAttempt
        hard["Not Attempted"]=hard["Total Questions"]-hardAttempt
        easy["Positive Score"]=easyPos
        med["Positive Score"]=medPos
        hard["Positive Score"]=hardPos
        easy["Negative Score"]=easyNeg
        med["Negative Score"]=medNeg
        hard["Negative Score"]=hardNeg
        easy["Total Marks Obtained"]=easyPos+easyNeg
        med["Total Marks Obtained"]=medPos+medNeg
        hard["Total Marks Obtained"]=hardPos+hardNeg
        return render(request,"resultanalysis.html",{"username":username,"quizid":quizid,"details":details,"easy":easy,"med":med,"hard":hard})
   
