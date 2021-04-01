from rest_framework import serializers
from authentication.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=6, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', ]

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        if not username.isalnum():
            raise serializers.ValidationError('The username should only consists of alphanumeric characters')
        if len(password) < 6:
            raise serializers.ValidationError('Make sure your password is at least 6 letters')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=4, write_only=True)
    password = serializers.CharField(max_length=64, min_length=6, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', ]

    # def validate(self, attrs):
    #     username = attrs.get('username', '')
    #     password = attrs.get('password', '')
    #     user = authenticate(username=username, password=password)
    #     if user:
    #         if not user.is_active:
    #             raise AuthenticationFailed('Account disabled')
    #     if not user:
    #         raise AuthenticationFailed('Invalid credentials, try again')
    #     return attrs
