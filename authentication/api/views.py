from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from authentication.models import User
from authentication.utils import Util
from .serializers import RegisterSerializer, LoginSerializer
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import jwt


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        refresh = RefreshToken.for_user(user)
        access = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        absurl = 'http://' + current_site + relative_link + "?token=" + str(access)
        email_body = 'Hi ' + user.username + ', click the link below to verify your email\n' + absurl
        message = {'email_body': email_body, 'email_subject': 'Verify your email', 'to_email': (user.email,)}
        Util.send_email(message)
        user_data['refresh'] = str(refresh)
        user_data['access'] = str(access)
        user_data['id'] = user.id
        user_data['is_verified'] = user.is_verified
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token')
        secret_key = settings.SECRET_KEY
        try:
            payload = jwt.decode(token, secret_key)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                email_body = 'Your email was successfully verified. Thanks for registering.'
                message = {'email_body': email_body, 'email_subject': 'Your email was verified.',
                           'to_email': (user.email,)}
                Util.send_email(message)
                return Response({'status': 'Successfully verified'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = str(request.data['username']).lower()
        try:
            user = User.objects.get(username=username)
            refresh = RefreshToken.for_user(user)
            access = RefreshToken.for_user(user).access_token
            return Response({'refresh': str(refresh), 'access': str(access), 'user_id': user.id,
                             'username': user.username, 'email': user.email, 'first_name': user.first_name,
                             'last_name': user.last_name, 'is_verified': user.is_verified, 'role':user.role}, status=status.HTTP_200_OK) 
        except ObjectDoesNotExist:
            raise ValidationError({"message": "User not found with the given email."})
