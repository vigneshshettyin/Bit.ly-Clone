from rest_framework import serializers
from .models import Link
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login')


class LinkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Link
        fields = '__all__'

        extra_kwargs = {
            'clicks': {'read_only': True},
        }


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user is None:
            raise serializers.ValidationError('Invalid email')
        if not user.check_password(data['password']):
            raise serializers.ValidationError('Invalid password')
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')
        password2 = validated_data.get('password2')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        user = User(username=username, email=email)
        if password == password2:
            user.set_password(password)
            user.save()
            return user
        else:
            raise serializers.ValidationError({
                'error': 'Passwords do not match'
            })
