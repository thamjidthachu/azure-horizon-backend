from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string
from rest_framework import status, generics
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError

from django.db.models import Q
from .serializers import UserSerializer, RegisterSerializer, ForgotPasswordSerializer, PasswordResetSerializer
from utils.email import send_email_message

User = get_user_model()


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response({'status': 'ok', 'application': 'Azure Horizon', "version": "0.0.1"}, status=status.HTTP_200_OK)


class UserCheckView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        email = request.query_params.get('email')
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                return Response({'status': True}, status=status.HTTP_200_OK)

        if email:
            user = User.objects.filter(email=email).first()
            if user:
                return Response({'status': True}, status=status.HTTP_200_OK)

        return Response({'status': False}, status=status.HTTP_404_NOT_FOUND)

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please check your email for login credentials.'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Please provide both username/email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(Q(email=username) | Q(username=username)).first()
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        email = user.email
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid Credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user data
        user_serializer = UserSerializer(user, context={'request': request})

        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        try:
            # Blacklist refresh token (if provided)
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Blacklist access token (from Authorization header)
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token_str = auth_header.split(" ")[1]
                access_token = AccessToken(access_token_str)

                # Store access token in blacklist
                outstanding_token, _ = OutstandingToken.objects.get_or_create(
                    jti=access_token["jti"],
                    defaults={
                        "token": access_token_str,
                        "expires_at": access_token["exp"],
                        "user": request.user,
                    },
                )
                BlacklistedToken.objects.get_or_create(token=outstanding_token)

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        return {'request': self.request}

class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.filter(Q(email=username) | Q(username=username)).first()
        token = get_random_string(32)
        user.reset_token = token
        user.save(update_fields=['reset_token'])
        url = f"{settings.BASE_FRONTEND_URL}/reset-password/?token={token}&username={user.username}"
        # Send reset email
        # send_email_message.delay(
        send_email_message(
            subject="Password Reset Request",
            template_name="password-reset.html",
            context={"reset_url": url, "email": user.email, "full_name": user.full_name},
            recipient_list=[user.email]
        )
        return Response({"message": "Password reset instructions sent to your email."}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        try:
            user = User.objects.filter(
                (Q(email=username) | Q(username=username)) & Q(reset_token=token)
                ).first()
        except User.DoesNotExist:
            return Response({"error": "Invalid token or email/username."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.reset_token = None
        user.save(update_fields=['password', 'reset_token'])
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)