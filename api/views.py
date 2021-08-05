from django.views.generic.base import TemplateResponseMixin
from .serializers import *
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,ListCreateAPIView
from rest_framework.views import APIView
from .permissions import *
from django.db.models import Avg
from rest_framework.permissions import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import *
from .forms import *
from authentication.models import User, UserGroup
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.http import HttpResponse, response
import json
from django.contrib.auth.decorators import login_required
from datetime import datetime
import regex as re
from django.shortcuts import render
import pandas as pd
from csv import writer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse, redirect,Http404
from rest_framework.decorators import api_view
import requests
from django.core.mail import EmailMessage

# Create your views here.


class HomeView(GenericAPIView):
	permission_classes = [AllowAny]

	def get(self, request):
		return Response("Hey, Welcome to Quiz Platform!")

class QuizGroupCreateView(GenericAPIView):
	serializer_class = QuizGroupSerializer
	permission_classes = [IsAuthenticated,IsTeacher]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		data = request.data
		serializer = self.serializer_class(data=data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

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
				quiz_questions = quiz.question.distinct()
				q_id_set = set()
				questions = []
				quest = AddQuestion.objects.filter(quiz_id=quiz.id).order_by("createdOn")
				for i in quest:
					q_id_set.add(str(i.question.id))
					ques_serializer = QuestionSerializer(i.question)
					questions.append(ques_serializer.data)
				for i in quiz_questions:
					if str(i.id) not in q_id_set:
						q_id_set.add(str(i.id))
						ques_serializer = QuestionSerializer(i)
						questions.append(ques_serializer.data)
				for i in questions:
					try:
						options = i["option"].replace("'",'"')
						options = json.loads(options)
					except Exception as e:
						options = i["option"]
					temp=[]
					if options is None or options == "" or options=={}:
						i["numberOfInputs"]=len(i["answer"])
						i["option"] = None
					else:
						for j in options:
							temp.append(options[j])
						i["option"] = temp
					i["answer"] = None
				result['quiz_details'] = serializer.data
				result['quiz_questions'] = questions
				result['feedback'] = False
				try:
					ques=feedbackQuestions.objects.get(quiz_id=quiz_id)
					if len(ques.question) != 0:
						result['feedback'] = True
				except:
					pass
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
		gid = data["Quizgroup"]
		ser = serializer.data
		try:
			gr = QuizGroup.objects.get(id=gid)
			id = ser["id"]
			quiz = Quiz.objects.get(id=id)
			quiz.quizgroup_id = gid
			quiz.save()
		except:
			return Response({'data':ser,'message':'No quiz group with the given id'},status=status.HTTP_400_BAD_REQUEST)
		return Response(ser, status=status.HTTP_200_OK)


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
		time_taken = request.data['time_taken']/1000
		seconds=(time_taken/1000)%60
		seconds = int(seconds)
		minutes=(time_taken/(1000*60))%60
		minutes = int(minutes)
		hours=(time_taken/(1000*60*60))%24
		time_taken = "%d:%02d:%02d" % (hours, minutes, seconds)
		request.data['time_taken'] = time_taken
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
			question_ids = []
			for aq in AddQuestion.objects.filter(quiz=quiz.id):
				question_ids.append(aq.question_id) 
			for i in Question.objects.filter(id__in = question_ids):
				print(i.question_type,"||",i.id, end="||")
				if i.question_type == 'Single Correct' or i.question_type == 'True False' or i.question_type == 'Assertion Reason':
					print(1,"-",res_dict[str(i.id)],"||", i.answer, end="||")
					if res_dict[str(i.id)] == "":
						marks += 0
					else:
						if i.option[str(res_dict[str(i.id)])].strip() == i.answer['1'].strip():
							marks += i.correct_marks
							print("correct")
						else:
							marks -= i.negative_marks
							print("incorrect")
				elif i.question_type == 'Input Type':
					print(2,"-",res_dict[str(i.id)],"||", i.answer,end="||")
					if res_dict[str(i.id)] == "":
						marks += 0
					else:
						if res_dict[str(i.id)].strip().split(',') == list(i.answer.values()):
							marks += i.correct_marks
							print("correct")
						else:
							marks -= i.negative_marks
							print("incorrect")
				else:
					print(3,"-",res_dict[str(i.id)],"||", i.answer,end="||")
					if res_dict[str(i.id)] == "":
						marks += 0
					else:
						response_answers = set()
						for j in res_dict[str(i.id)].split(","):
							response_answers.add(i.option[str(j)].strip())
						if response_answers == set(i.answer.values()):
							marks += i.correct_marks
							print("correct")
						else:
							marks -= i.negative_marks
							print("incorrect")
			quizobject = QuizResponse.objects.filter(quiz=quiz_id, user=user_id)
			quizobject.update(marks=marks)
			# time_taken = quiz.duration - time_taken
			# quizobject.update(time_taken=time_taken)
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
						if i.question_type == 'Single Correct':
							if res_dict[str(i.id)] == "":
								marks += 0
							else:
								if i.option[str(res_dict[str(i.id)])].strip() == i.answer['1'].strip():
									marks += i.correct_marks
								else:
									marks -= i.negative_marks
						elif i.question_type == 'Input Type':
							if res_dict[str(i.id)] == "":
								marks += 0
							else:
								if res_dict[str(i.id)].strip() == i.answer['1'].strip():
									marks += i.correct_marks
								else:
									marks -= i.negative_marks
						else:
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

    serializer_class = AssignQuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data
            try:
                aq = AssignQuiz.objects.get(quiz_id=data["quiz"])
                for u in aq.user.all():
                    if data["user"] == str(u.id):
                        return Response({"Student already added"})
                        break
                else:
                    aq.user.add(data['user'])
                    aq.save()
                    return Response({"message": "Student has been added to the quiz"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "Student has been added to the quiz"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Some error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                            
class AssignGroup(GenericAPIView):
    serializer_class = AssignQuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = request.data
            try:
                aq = AssignQuiz.objects.get(quiz_id=data["quiz"])
                if data["group"] in aq.group.all():
                    return Response({"Group already added"})
                else:
                    aq.group.add(data['group'])
                    aq.save()
                    return Response({"message": "Group has been added to the quiz"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "Group has been added to the quiz"}, status=status.HTTP_200_OK)
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
				quizgroups = QuizGroup.objects.all()
				quiz_groups  = []
				for qgrp in quizgroups:
					self.queryset = Quiz.objects.filter(creator=user, quizgroup=qgrp)
					serializer = self.serializer_class(self.queryset, many=True)
					quizzes = serializer.data
					upcoming,active,completed = [],[],[]
					for i in range(len(quizzes)):
						starttime = datetime.strptime(quizzes[i]["starttime"],"%Y-%m-%dT%H:%M:%S%z").timestamp()
						endtime = datetime.strptime(quizzes[i]["endtime"],"%Y-%m-%dT%H:%M:%S%z").timestamp()
						currenttime = datetime.now().timestamp()
						if starttime > currenttime:
							upcoming.append(quizzes[i])
						elif starttime < currenttime and endtime > currenttime:
							active.append(quizzes[i])
						else:
							completed.append(quizzes[i])
						user_id = quizzes[i]['creator']
						try:
							user = User.objects.get(id=user_id)
							quizzes[i]['creator_username'] = user.username
						except ObjectDoesNotExist:
							raise ValidationError({"message": "User do not found"})
					quiz_groups.append({'name':qgrp.title,"id":qgrp.id,"upcoming":upcoming,"active":active,"completed":completed})
				return Response(quiz_groups)
			else:
				quiz_groups = []
				usergroups = UserGroup.objects.filter(user=userid)
				assign_quiz_group = AssignQuizGroup.objects.filter(user_group__in = usergroups).values_list('quiz_group', flat=True)
				assign_quiz_group = [str(o) for o in assign_quiz_group]
				quizgroups = QuizGroup.objects.filter(id__in=assign_quiz_group)
				for group in quizgroups:
					quizzes = Quiz.objects.filter(quizgroup = group)
					upcoming,active,attempted,missed = [],[],[],[]
					for quiz in quizzes:
						starttime = quiz.starttime.timestamp()
						endtime = quiz.endtime.timestamp()
						currenttime = datetime.now().timestamp()
						if starttime > currenttime:
							upcoming.append(QuizSerializer(quiz).data)
						elif starttime < currenttime and endtime > currenttime:
							try:
								QuizResponse.objects.get(user=userid,quiz=quiz.id)
								try:
									sr = save_result.objects.get(user__id=userid, quizid = str(quiz.id))
								except:
									pass
								attempted.append(QuizSerializer(quiz).data)
							except:
								active.append(QuizSerializer(quiz).data)
						else:
							try:
								QuizResponse.objects.get(user=userid,quiz=quiz.id)
								try:
									sr = save_result.objects.get(user__id=userid, quizid = str(quiz.id))
								except:
									pass
								attempted.append(QuizSerializer(quiz).data)
							except:
								missed.append(QuizSerializer(quiz).data)
						creator_id = quiz.creator.id
						try:
							user = User.objects.get(id=creator_id)
						except ObjectDoesNotExist:
							raise ValidationError({"message": "User do not found"})
					groups = {'name':group.title,"upcoming":upcoming,"active":active,"attempted":attempted,"missed":missed}
					quiz_groups.append(groups)
				return Response(quiz_groups)
		except ObjectDoesNotExist:
			return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

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
                        quiz_response = QuizResponse.objects.get(quiz=quiz, user=user)
                        return Response({"message": "You have already attempted the test"},status=status.HTTP_400_BAD_REQUEST)
                    except:
                        return Response({"message": "Success"}, status=status.HTTP_200_OK)
                except:
                    return Response({"message": "User not found with the given id"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "This quiz is either not open yet or is now closed"}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Quiz not found with the given id"}, status=status.HTTP_404_NOT_FOUND)

class createFeedback(ListCreateAPIView):
	serializer_class = FeedBackSerializer
	queryset=FeedBackForm.objects.all()

class feedbackQuestionsapi(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self,request,format=None):
		data=request.data
		serializer=FeedbackQuesSerializer(data=request.data)
		query=feedbackQuestions.objects.filter(quiz_id=data['quiz_id'])
		if query.exists():
			query.delete()
		if serializer.is_valid():
			serializer.save()
			return Response({'msg':"created"},status=status.HTTP_201_CREATED)
		return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)	
	
	def get(self,request,quiz_id,format=None):
		ques=feedbackQuestions.objects.get(quiz_id=quiz_id)
		serializer=FeedbackQuesSerializer(ques)
		data = serializer.data
		return Response(data, status=status.HTTP_200_OK)


	def patch(self,request,question_id,format=None):
		ques=feedbackQuestions.objects.get(id=question_id)
		serializer=FeedbackQuesSerializer(ques,data=request.data,partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({"msg":"question updated"})
		return Response(serializer.errors)
	

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
		dificultydict={}
		for key, value in res_dict.items():
			ques = Question.objects.get(id=key)
			if ques.dificulty_tag == "Easy":
				easyTot += 1
			elif ques.dificulty_tag == "Medium":
				medTot += 1
				try:
					if ques.subject_tag:
						try:
							if dificultydict[ques.subject_tag]:
								try:
									if dificultydict[ques.subject_tag]["Medium"]:
										dificultydict[ques.subject_tag]["Medium"]+=1
								except:
									dificultydict[ques.subject_tag]["Medium"]=1
						except:
							dificultydict[ques.subject_tag]={}
							
				except:
					pass
			elif ques.dificulty_tag == "Hard":
				hardTot += 1
				try:
					if ques.subject_tag:
						try:
							if dificultydict[ques.subject_tag]:
								try:
									if dificultydict[ques.subject_tag]["Hard"]:
										dificultydict[ques.subject_tag]["Hard"]+=1
								except:
									dificultydict[ques.subject_tag]["Hard"]=1
						except:
							dificultydict[ques.subject_tag]={}
				except:
					pass
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

	def get(self, request, username, quizid):
		result = {}
		try:
			user = User.objects.get(username=username)
		except:
			error = "user does not exist"
			return Response({"message": error})
		try:
			quizes = QuizResponse.objects.filter(quiz_id=quizid,user=user.id)[0]
		except:
			error = "The user has not attempted this quiz"
			return Response({"message": error})
		q = QuizResponse.objects.get(quiz_id=quizid,user=user.id)
		arr = []
		quizobj = Quiz.objects.filter(title=q.quiz)[0]
		totalquestion = 0
		attemptedquestion = 0
		nonattempted = 0
		correctquestion = 0
		wrongquestion = 0
		totalmarks = 0
		dic = {}
		quesdic = []
		difiarr=[]
		dificultydict={}
		response = q.response.replace("'", '"')
		res_dict = json.loads(response)
		for ques in res_dict:
			totalquestion += 1
			obj = Question.objects.get(id=str(ques))

			# Input Type Question
			if obj.question_type == 'Input Type':
				temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer": ",".join(list(obj.answer.values())),"your answer": res_dict[ques].strip()}
				quesdic.append(temp_dict)
				if res_dict[ques] != "":
					attemptedquestion += 1
					if (list(obj.answer.values()) == res_dict[ques].strip().split(",")):
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

				# Difficulty Dictionary
				try:
					if dificultydict[obj.subject_tag][obj.dificulty_tag]:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]+=1
						if flag=="True":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
						elif flag=="False":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
						else:
							dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1
				except:
					dificultydict[obj.subject_tag]={}
					dificultydict[obj.subject_tag][obj.dificulty_tag]={}
					dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]=1
					dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]=0
					if flag=="True":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
					elif flag=="False":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
					else:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1

			# Multiple Answer Correct
			elif obj.question_type == 'Multiple Correct':
				response_answers = set()
				for j in res_dict[str(obj.id)].split(","):
						response_answers.add(obj.option[str(j)].strip())
				temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer": ",".join(list(obj.answer.values())),"your answer": ",".join(response_answers)}
				quesdic.append(temp_dict)
				if res_dict[ques] != "":
					attemptedquestion += 1					
					if (set(obj.answer.values()) == response_answers):
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

				# Difficulty Dictionary
				try:
					if dificultydict[obj.subject_tag][obj.dificulty_tag]:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]+=1
						if flag=="True":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
						elif flag=="False":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
						else:
							dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1
				except:
					dificultydict[obj.subject_tag]={}
					dificultydict[obj.subject_tag][obj.dificulty_tag]={}
					dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]=1
					dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]=0
					if flag=="True":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
					elif flag=="False":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
					else:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1

			# Single Correct, True or False, Assertion Reason Type Questions
			else:
				if(type(obj.option) is str):
					temp = obj.option.replace("'",'"')
					temp = json.loads(temp)
				else:
					temp = obj.option
				if res_dict[ques] != "":
					try:
						temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer": temp[str(obj.answer['1'])],"your answer":temp[str(res_dict[ques])]}
					except:
						temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer": str(obj.answer['1']),"your answer": str(obj.option[str(res_dict[ques])])}
				else:
					try:
						temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer":  temp[str(obj.answer['1'])],"your answer": ""}
					except:
						temp_dict = {"question_number":totalquestion,"question":obj.question,"correct answer": str(obj.answer['1']),"your answer": ""}
				quesdic.append(temp_dict)
				if res_dict[ques] != "":
					attemptedquestion += 1
					if (str(obj.answer['1']) == str(res_dict[ques])) or (str(temp[str(res_dict[ques])]) == str(obj.answer['1'])):
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
				try:
					if dificultydict[obj.subject_tag]:
						pass
				except:
					dificultydict[obj.subject_tag]={}

				try:
					if dificultydict[obj.subject_tag][obj.dificulty_tag]:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]+=1
						if flag=="True":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
						elif flag=="False":
							dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
						else:
							dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1
				except:
					dificultydict[obj.subject_tag][obj.dificulty_tag]={}
					dificultydict[obj.subject_tag][obj.dificulty_tag]["total_questions"]=1
					dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]=0
					dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]=0
					if flag=="True":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["correct"]+=1
					elif flag=="False":
						dificultydict[obj.subject_tag][obj.dificulty_tag]["incorrect"]+=1
					else:
						dificultydict[obj.subject_tag][obj.dificulty_tag]["not_attempted"]+=1
			subjecttag = obj.subject_tag
			try:
				if dic["subject: " + subjecttag]:
					pass
			except:
				dic["subject: " + subjecttag] = {}
			try:
				if dic["subject: " + subjecttag]["total_questions"]:
					pass
			except:
				dic["subject: " + subjecttag]["total_questions"] = 0
			try:
				if dic["subject: " + subjecttag]["correct_questions"]:
					pass
			except:
				dic["subject: " + subjecttag]["correct_questions"] = 0
			try:
				if dic["subject: " + subjecttag]["incorrect"]:
					pass
			except:
				dic["subject: " + subjecttag]["incorrect"] = 0
			try:
				if dic["subject: " + subjecttag]["not_attempted"] :
					pass
			except:
				dic["subject: " + subjecttag]["not_attempted"] = 0
			
			
			if subjecttag is not None and subjecttag.strip() != "":
				dic["subject: " + subjecttag]["total_questions"] += 1
				if flag == "True":
					dic["subject: " + subjecttag]["correct_questions"] += 1
				elif flag == "False":
					dic["subject: " + subjecttag]["incorrect"] += 1
				else:
					dic["subject: " + subjecttag]["not_attempted"] += 1
			topictag = obj.subtopic_tag
			try:
				if dic["topic: " + topictag]:
					pass
			except:
				dic["topic: " + topictag] = {}
			try:
				if dic["topic: " + topictag]["total_questions"]:
					pass
			except:
				dic["topic: " + topictag]["total_questions"] = 0
			try:
				if dic["topic: " + topictag]["correct_questions"]:
					pass
			except:
				dic["topic: " + topictag]["correct_questions"] = 0
			try:
				if dic["topic: " + topictag]["incorrect"]:
					pass
			except:
				dic["topic: " + topictag]["incorrect"] = 0
			try:
				if dic["topic: " + topictag]["not_attempted"] :
					pass
			except:
				dic["topic: " + topictag]["not_attempted"] = 0
			if topictag is not None and topictag.strip() != "":
					dic["topic: " + topictag]["total_questions"] += 1
					if flag == "True":
						dic["topic: " + topictag]["correct_questions"] += 1
					elif flag=="False":
						dic["topic: " + topictag]["incorrect"] += 1
					else:
						dic["topic: " + topictag]["not_attempted"] += 1
			subtopictag = obj.topic_tag
			try:
				if dic["subtopic: " + subtopictag]:
					pass
			except:
				dic["subtopic: " + subtopictag] = {}
			try:
				if dic["subtopic: " + subtopictag]["total_questions"]:
					pass
			except:
				dic["subtopic: " + subtopictag]["total_questions"] = 0
			try:
				if dic["subtopic: " + subtopictag]["correct_questions"]:
					pass
			except:
				dic["subtopic: " + subtopictag]["correct_questions"] = 0
			try:
				if dic["subtopic: " + subtopictag]["incorrect"]:
					pass
			except:
				dic["subtopic: " + subtopictag]["incorrect"] = 0
			try:
				if dic["subtopic: " + subtopictag]["not_attempted"] :
					pass
			except:
				dic["subtopic: " + subtopictag]["not_attempted"] = 0
			if subtopictag is not None and subtopictag.strip() != "":
					dic["subtopic: " + subtopictag]["total_questions"] += 1
					if flag == "True":
						dic["subtopic: " + subtopictag]["correct_questions"] += 1
					elif flag=="False":
						dic["subtopic: " + subtopictag]["incorrect"] += 1
					else:
						dic["subtopic: " + subtopictag]["not_attempted"] += 1

			skilltag = obj.skill
			try:
				if dic["skill: " + skilltag]:
					pass
			except:
				dic["skill: " + skilltag] = {}
			try:
				if dic["skill: " + skilltag]["total_questions"]:
					pass
			except:
				dic["skill: " + skilltag]["total_questions"] = 0
			try:
				if dic["skill: " + skilltag]["correct_questions"]:
					pass
			except:
				dic["skill: " + skilltag]["correct_questions"] = 0
			try:
				if dic["skill: " + skilltag]["incorrect"]:
					pass
			except:
				dic["skill: " + skilltag]["incorrect"] = 0
			try:
				if dic["skill: " + skilltag]["not_attempted"] :
					pass
			except:
				dic["skill: " + skilltag]["not_attempted"] = 0
			if skilltag is not None and skilltag.strip() != "":
					dic["skill: " + skilltag]["total_questions"] += 1
					if flag == "True":
						dic["skill: " + skilltag]["correct_questions"] += 1
					elif flag=="False":
						dic["skill: " + skilltag]["incorrect"] += 1
					else:
						dic["skill: " + skilltag]["not_attempted"] += 1
			dificultytag = obj.dificulty_tag
			try:
				if dic["dificulty: " + dificultytag]:
					pass
			except:
				dic["dificulty: " + dificultytag] = {}
			try:
				if dic["dificulty: " + dificultytag]["total_questions"]:
					pass
			except:
				dic["dificulty: " + dificultytag]["total_questions"] = 0
			try:
				if dic["dificulty: " + dificultytag]["correct_questions"]:
					pass
			except:
				dic["dificulty: " + dificultytag]["correct_questions"] = 0
			try:
				if dic["dificulty: " + dificultytag]["incorrect"]:
					pass
			except:
				dic["dificulty: " + dificultytag]["incorrect"] = 0
			try:
				if dic["dificulty: " + dificultytag]["not_attempted"] :
					pass
			except:
				dic["dificulty: " + dificultytag]["not_attempted"] = 0
			if  dificultytag is not None and dificultytag.strip() != "":
					dic["dificulty: " + dificultytag]["total_questions"] += 1
					if flag == "True":
						dic["dificulty: " + dificultytag]["correct_questions"] += 1
					elif flag=="False":
						dic["dificulty: " + dificultytag]["incorrect"] += 1
					else:
						dic["dificulty: " + dificultytag]["not_attempted"] += 1
		difiarr.append(dificultydict)
		result = {"Quiz Name": quizobj.title + " by " + str(quizobj.creator), "totalquestion": totalquestion,"correctquestion": correctquestion, "incorrectquestion": wrongquestion,"attempted": attemptedquestion, "not_attempted": nonattempted, "marks_obtained": totalmarks,"responses": quesdic, "analysis": dic,"subjectwise_difficulty":difiarr}
		arr.append(result)
		return Response({"data": result})

class CreateExcelForScore(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        is_request=run_excel_task.objects.all()
        while is_request:
            run_excel_model=is_request[0]
            quizid=run_excel_model.quizid
            email=run_excel_model.email_send
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
                    print(f'https://api.progressiveminds.in/api/getresult/{user}/{quizid}')
                    data = requests.get(f'https://api.progressiveminds.in/api/getresult/{user}/{quizid}').json()['data']
                    ## basic analysis
                    new_result = [sno, user, data['Quiz Name'], data['totalquestion'], data['correctquestion'],
                                data['incorrectquestion'],
                                data['attempted'], data['not_attempted'], data['marks_obtained']]
                    writer_object.writerow(new_result)

					# question analysis
                    for datas in data['responses']:
                        new_result_question = [sno, user, datas['question_number'], datas['question'], datas['correct answer'], datas['your answer']]
                        writer_object_question.writerow(new_result_question)
                    for tag, resp in data['analysis'].items():
                        new_result_tag = [sno, user, tag, resp['total_questions'], resp['correct_questions'],resp['incorrect'],resp['not_attempted']]
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
            print('******** bas khatam *********')
            with open("media/result_response/Result.xlsx", "rb") as excel:
                content = excel.read()
            response = HttpResponse(content=content, content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Result.xlsx"'
            q=Quiz.objects.get(id=quizid)
            emailmessage = EmailMessage('Result For Quiz '+q.title, 'Your Excel sheet is ready.', 'skrkmk212@gmail.com',
                [email])
            emailmessage.attach('Result.xlsx',content,'application/ms-excel')
            emailmessage.send(fail_silently=False)
            run_excel_model.delete()
            is_request=run_excel_task.objects.all()
            return HttpResponse("Done")
        return HttpResponse("No Task")

class RunExcelCreateView(GenericAPIView):
    serializer_class = RunExcelTaskSerializer
    permission_classes = [AllowAny]
    # authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return HttpResponse("Your request is in process.You will be notified via email within 24 hours. If not please contact admin.")
    

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
			quiz_questions.remove(Question.objects.get(id=question_id))
		except Exception as e:
			print(e)
			return Response({"message": "Cannot delete the question"})
		return Response({"message": "Question removed from the quiz successfully"})


class AddQuestionToQuiz(APIView):

	serializer_class = QuizResponseSerializer
	permission_classes = [IsAuthenticated,IsTeacher]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		try:
			quest_ids = request.data['quest_id']
			error_ids = []
			i = 0
			for q in quest_ids:
				try:
					AddQuestion.objects.create(quiz_id=request.data['quiz_id'],question_id=str(q))
					i = i +1
				except Exception:
					error_ids.append(q)
					#return Response({"message": f"{q}, not valid"}, status=400)
			print("Error Question IDs ",error_ids)
			return Response({"message": f"{i} Questions added successfully"}, status=200)
		except Exception:
			return Response({"message": "something went wrong"}, status=400)

class QuestionBankListView(GenericAPIView):
    permission_classes = [IsAuthenticated,IsTeacher]
    authentication_classes = [JWTAuthentication]
    serializer_class = QuestionSerializer

    def get(self,request,quizid):
        given_quiz=Quiz.objects.get(id=quizid)
        qu=AddQuestion.objects.filter(quiz_id=quizid)
        already=set()
        for i in qu:
            already.add(str(i.question.id))
        for i in given_quiz.question.all():
            already.add(i.id)
        already = list(already)
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
                topictags = Question.objects.filter(subject_tag=subject).values_list("topic_tag").distinct()
                for j in topictags:
                    if (j[0]!="" and j[0].strip() != ""):
                        topic = j[0]
                        temp1={}
                        temp1["name"]=j[0]
                        subtopicstags = Question.objects.filter(subject_tag=subject, topic_tag=topic).values_list("subtopic_tag").distinct()
                        subtopiclist = [k[0] for k in subtopicstags if (k[0].strip() != "" and k[0]!="")]
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
	if request.method == "POST":
		#print(request.POST)
		post_data = request.POST
		data = {}
		if post_data['questiontype'] != 'Input Type':
			data['totaloption'] = post_data['totaloption']
			data['options'] = dict()
			for i in range(1,int(data['totaloption'])+1):
				data['options'][str(i)] = post_data['option'+str(i)].strip()

		if post_data['questiontype'] in ['Input Type','Multiple Correct']:
			pass
		
		for i in range(1, int(post_data['totalquestion'])+1):
			print('QuestionCreated')
			j=1
			data['answer'] = {}
			for ans in post_data['answer'+str(i)].split(','):
				data['answer'][str(j)] = ans.strip()
				j = j + 1
			obj = Question.objects.create(question_type = post_data["questiontype"], question=post_data["question"+str(i)],
										correct_marks=post_data['positive_score'],negative_marks=post_data['negative_score'],
										subject_tag=post_data['subject_tag'], topic_tag=post_data['topic_tag'],subtopic_tag=post_data['subtopic_tag'],
										dificulty_tag=post_data['dificulty_tag'+str(i)],skill=post_data['skill_tag'+str(i)])

			if post_data['questiontype'] != 'Input Type':
				obj.option = data['options']
			obj.answer = data['answer']
			if post_data['questiontype'] == 'Assertion Reason':
				obj.passage = post_data['passage']
			obj.save()
		return redirect("/questionbank")
	dificulty = [("Easy"),("Medium"),("Hard")]
	return render(request,"addQuestions.html",{"dificulty":dificulty})


def editquestion(request,qid):

	if request.method == "POST":
		option = {}
		for i in range(1,int(request.POST['totaloption'])+1):
			option[str(i)] = request.POST['option'+str(i)]
		answer = request.POST['answer'].split(',')
		a= {}
		for i in range(1,len(answer)+1):
			a[str(i)] = answer[i-1]
		answer = a

		id =  request.POST["id"]
		questionobj = Question.objects.get(id=id)
		questionobj.answer = answer
		questionobj.subject_tag = request.POST['subject_tag']
		questionobj.topic_tag = request.POST['topic_tag']
		questionobj.subtopic_tag = request.POST['subtopic_tag']
		questionobj.dificulty_tag = request.POST['dificulty_tag']
		questionobj.skill = request.POST['skill_tag']
		questionobj.question = request.POST['question']
		questionobj.option = option
		questionobj.correct_marks = request.POST['positive_score']
		questionobj.negative_marks = request.POST['negative_score']
		questionobj.save()
		return redirect("/questionbank")
	try:
		question = Question.objects.get(id=qid)
	except:
		raise Http404
	options = []
	noinputs = len(question.answer)
	try:
		for v in question.option.values():
			options.append(v)

	except:
		pass
	answer = ','.join(question.answer.values())
	dificulty = [("Easy"),("Medium"),("Hard")]
	questiontypes = ["Multiple Correct","True False","Input Type","Single Correct","Assertion Reason"]
	return render(request,"editQuestion.html",{'question':question,"questiontypes":questiontypes,'options':options,'answers':answer,'dificulty':dificulty, 'noinputs':noinputs})


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
	url = "https://api.progressiveminds.in/media/" + path
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
def getaverage(quizid):
	avscore=[]
	avcorrect=[]
	avincorrect=[]
	avattempted=[]
	avnotattempted=[]
	users = QuizResponse.objects.filter(quiz_id=quizid).values_list('user', flat=True)
	for user in users:
		userobj = User.objects.get(id=user)
		try:
			data = requests.get(f'https://api.progressiveminds.in/api/getresult/{userobj.username}/{quizid}').json()['data']
		except:
			return Response({"message":"No Response found"}, status=status.HTTP_404_NOT_FOUND)
		avscore.append(int(data['marks_obtained']))
		avcorrect.append(int(data['correctquestion']))
		avincorrect.append(int(data['incorrectquestion']))
		avattempted.append(int(data['attempted']))
		avnotattempted.append(int(data['not_attempted']))
	av_score=sum(avscore)/len(avscore)
	av_correct=sum(avcorrect)/len(avcorrect)
	av_incorrect=sum(avincorrect)/len(avincorrect)
	av_attempted=sum(avattempted)/len(avattempted)
	av_notattempted=sum(avnotattempted)/len(avnotattempted)
	avdata={"Quiz Name": "abc" ,
				"totalquestion": data['totalquestion'],
				"correctquestion": av_correct,
				"incorrectquestion": av_incorrect,
				"attempted": av_attempted,
				"not_attempted": av_notattempted,
				"marks_obtained": av_score}
	return avdata
class getScorecard(APIView):
	permission_classes = [AllowAny]

	def get(self, request,quizid):
		quiz_name = ""
		avscore=[]
		avcorrect=[]
		avincorrect=[]
		avattempted=[]
		avnotattempted=[]
		topperDone = False
		users = QuizResponse.objects.filter(quiz_id=quizid).values_list('user', flat=True)
		for user in users:
			userobj = User.objects.get(id=user)
			try:
				data = requests.get(f'https://api.progressiveminds.in/api/getresult/{userobj.username}/{quizid}').json()['data']
			except:
				return Response({"message":"No Response found"}, status=status.HTTP_404_NOT_FOUND)
			if quiz_name == "":
				quiz_name = data['Quiz Name']
			avscore.append(int(data['marks_obtained']))
			avcorrect.append(int(data['correctquestion']))
			avincorrect.append(int(data['incorrectquestion']))
			avattempted.append(int(data['attempted']))
			avnotattempted.append(int(data['not_attempted']))
			try:
				u=save_result.objects.get(user=userobj,quizid=quizid)
				u.data=data
				u.quizname=quiz_name
				u.score=data['marks_obtained']
				u.save()
			except:
				save_result.objects.create(user=userobj,data=data,quizid=quizid,quizname=quiz_name,score=data['marks_obtained'])
		av_score=sum(avscore)/len(avscore)
		av_correct=sum(avcorrect)/len(avcorrect)
		av_incorrect=sum(avincorrect)/len(avincorrect)
		av_attempted=sum(avattempted)/len(avattempted)
		av_notattempted=sum(avnotattempted)/len(avnotattempted)
		avscore=sorted(avscore, reverse=True)
		for user in users:
			userobj = User.objects.get(id=user)
			obj=save_result.objects.get(quizid=quizid,user=userobj)
			obj.rank=avscore.index(int(obj.score))+1
			obj.save()
			if str(obj.rank)=="1" and not topperDone:
				topperDone = True
				topper_data = {'Quiz Name': quiz_name,'totalquestion':obj.data['totalquestion'],'correctquestion':obj.data['correctquestion'],'incorrectquestion':obj.data['incorrectquestion'],
								'attempted':obj.data['attempted'],'notattempted':obj.data['not_attempted'],'marks_obtained':obj.data['marks_obtained']}
				try:
					u=save_result.objects.get(quizid=quizid,name="Topper")
					u.data=topper_data
					u.quizname=quiz_name
					u.score=obj.score
					u.save()
				except:
					save_result.objects.create(name="Topper",data=topper_data,quizid=quizid,quizname=quiz_name,score=obj.score,rank='1')
		avdata={"Quiz Name": quiz_name ,
				"totalquestion": data['totalquestion'],
				"correctquestion": av_correct,
				"incorrectquestion": av_incorrect,
				"attempted": av_attempted,
				"not_attempted": av_notattempted,
				"marks_obtained": av_score}
		try:
			u=save_result.objects.get(quizid=quizid,name="Average")
			u.data=avdata
			u.quizname=quiz_name
			u.score=av_score
			u.save()
		except:
			save_result.objects.create(name="Average",data=avdata,quizid=quizid,quizname=data['Quiz Name'],score=av_score,rank='N/A')
		return HttpResponse("done")	

def check_for_result(request):
	quiz=Quiz.objects.all()
	for a in quiz:
		if datetime.now().date() - a.endtime.date() >= timedelta(days=0) and (datetime.now().date() - a.endtime.date() <= timedelta(days=1)):
			q=save_result.objects.filter(quizid=a.id)
			print(a.id)
			requests.get(f'https://api.progressiveminds.in/api/requestScoreForResult/{a.id}')
		return HttpResponse("hua")

class get_student_result(GenericAPIView):
	permission_classes = [AllowAny]
	authentication_classes = [JWTAuthentication]
	
	def get(self,request, userid):
		try:
			user=User.objects.get(id=userid)
			self.queryset=save_result.objects.filter(user=user)
			# queryset = ''
			response=[]
			for i in self.queryset:
				response.append({'quizname':i.quizname,'id':str(i.id),'rank':i.rank})
			return Response(response, status=status.HTTP_200_OK)
		except:
			return Response({"message":"No quiz responses found"}, status=status.HTTP_404_NOT_FOUND)
		
class get_student_report(GenericAPIView):
	permission_classes = [AllowAny]

	def get(self,request,username,quizid):
			data = requests.get(f'https://api.progressiveminds.in/api/getresult/{username}/{quizid}').json()['data']
			quizzz = QuizResponse.objects.filter(quiz=quizid).order_by('-marks')
			quiz_average = QuizResponse.objects.filter(quiz=quizid).aggregate(Avg('marks'))['marks__avg']
			topper = quizzz.first()
			toLocaleUpperCase = QuizResponseSerializer(topper)
			topper_data = requests.get(f'https://api.progressiveminds.in/api/getresult/{topper.user}/{quizid}').json()['data']
			topper_data = {
				'Quiz Name': topper_data['Quiz Name'],
				'totalquestion':topper_data['totalquestion'],
				'correctquestion':topper_data['correctquestion'],
				'incorrectquestion':topper_data['incorrectquestion'],
				'attempted':topper_data['attempted'],
				'notattempted':topper_data['not_attempted'],
				'marks_obtained':topper_data['marks_obtained']
			}
			avdata = getaverage(quizid)
			count = 0
			for quiz_user in quizzz:
				count = count +1
				if quiz_user.user.username == username :
					data["rank"] = count
			result = {
				"data" : data,
				"topper": topper_data,
				"average": avdata
			}
			return Response(result, status=status.HTTP_200_OK)
class DelQuestion(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try:
			q=Question.objects.get(id=id)
			quiz=Quiz.objects.filter(question=q)
			for i in quiz:
				print(i)
				i.question.remove(q)
			q.delete()
			return Response({'message':'Question Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'Quiz not found'}, status=status.HTTP_400_BAD_REQUEST)

class DelQuiz(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try: 
			quiz = Quiz.objects.get(id=id)
			quiz.question.clear()
			quiz.delete()
			return Response({'message':'Quiz Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'Quiz not found'}, status=status.HTTP_400_BAD_REQUEST)

class DelQuizGroup(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try:
			qg = QuizGroup.objects.get(id=id)
			quiz=Quiz.objects.filter(quizgroup=qg)
			for i in quiz:
				i.quizgroup=None
				i.save()
			qg.delete()
			return Response({'message':'Quiz Group Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'Quiz Group not found'}, status=status.HTTP_400_BAD_REQUEST)

class DelAssignQuiz(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try:
			aq = AssignQuiz.objects.get(id=id)
			aq.group.clear()
			aq.user.clear()
			aq.delete()
			return Response({'message':'AssignQuiz Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'AssignQuiz not found'}, status=status.HTTP_400_BAD_REQUEST)

class DelUserGroup(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try:
			ug = UserGroup.objects.get(id=id)
			aq = AssignQuiz.objects.filter(group = ug)
			for i in aq:
				i.group.remove(ug)
			ug.delete()
			return Response({'message':'User Group Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'User Group not found'}, status=status.HTTP_400_BAD_REQUEST)

class DelUser(APIView):
	permission_classes = [IsAuthenticated,IsTeacher]

	def get(self,request,id):
		try:
			u = User.objects.get(id=id)
			aq = AssignQuiz.objects.filter(user = u)
			for i in aq:
				i.user.remove(u)
			ug = UserGroup.objects.filter(user=u)
			for i in ug:
				i.user.remove(u)
			u.delete()
			return Response({'message':'User Deleted'}, status=status.HTTP_200_OK)
		except:
			return Response({'message':'User not found'}, status=status.HTTP_400_BAD_REQUEST)
			

