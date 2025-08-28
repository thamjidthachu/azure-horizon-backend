from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings

from apps.authentication.models import User
from .tasks import send_welcome_email_task


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id',  'avatar', 'username', 'full_name', 'email', 'phone', 'gender', 'is_active',]
        read_only_fields = ['id', 'is_active']
    
    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('avatar','username', 'email', 'phone', 'password', 'password2', 'full_name')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})

        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Username is already in use."})

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 from the data
        validated_data.pop('password2', None)
        
        # Create user
        user = User.objects.create_user(
            avatar=validated_data.get('avatar'),
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            full_name=validated_data.get('full_name'),
            password=validated_data['password']
        )
        
        # Send welcome email asynchronously using Celery
        send_welcome_email_task.delay(
            user_id=user.id,
            username=user.username,
            email=user.email,
            password=validated_data['password']
        )
        
        return user

    @staticmethod
    def send_welcome_email(user, password):
        subject = 'Welcome to Our Resort'
        message = f"""
        Thank you for registering with us!
        
        Here are your login details:
        Username: {user.username}
        Email: {user.email}
        Password: {password}
        
        Please keep your credentials safe and do not share them with anyone.
        
        Best regards,
        The Resort Team
        """

        send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email])


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs