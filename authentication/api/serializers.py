from rest_framework import serializers
from authentication.models import User, UserGroup
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=6, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'role']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        role = attrs.get('role', 'Student')
        if not username.isalnum():
            raise serializers.ValidationError('The username should only consists of alphanumeric characters')
        if len(password) < 6:
            raise serializers.ValidationError('Make sure your password is at least 6 letters')
        if role not in ['Student', 'Teacher']:
            raise serializers.ValidationError("Role should be either Student or Teacher")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], 
            email=validated_data["email"], 
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        user.role = validated_data["role"]
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=4, write_only=True)
    password = serializers.CharField(max_length=64, min_length=6, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', ]

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        username = username.lower()
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                raise AuthenticationFailed('Account disabled')
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        return attrs

class UserGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGroup
        fields = '__all__'