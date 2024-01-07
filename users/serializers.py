from django.contrib.auth.models import User # User 모델
from django.contrib.auth.password_validation import validate_password # Django의 기본 pw 검증 도구
# from django.contrib.auth.backends

from rest_framework import serializers
from rest_framework.authtoken.models import Token # Token 모델

from rest_framework.validators import UniqueValidator # 이메일 중복 방지를 위한 검증 도구
from django.contrib.auth import authenticate
# 회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())], # 이메일에 대한 중복 검증
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # 비밀번호에 대한 검증
    )
    password2 = serializers.CharField( # 비밀번호 확인을 위한 필드
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ( 'email', 'password', 'password2')

    def validate(self, data): # password과 password2의 일치 여부 확인
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        
        return data

    def create(self, validated_data):
        # CREATE 요청에 대해 create 메서드를 오버라이딩하여, 유저를 생성하고 토큰도 생성하게 해준다.
        email = validated_data['email']
        username = email.split('@')[0]
        user = User.objects.create_user(
            email=email,
            username = username,
            # username = validated_data['email'].split('@')[0],
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        username = email.split('@')[0]
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return {
                    'access_token': token.key,
                    'username': user.username,  # Include the username in the response
                }

            raise serializers.ValidationError({"error": "Invalid credentials."})

        raise serializers.ValidationError({"error": "Email and password are required."})
