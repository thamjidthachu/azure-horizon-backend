from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import UserCheckView, RegisterView, LoginView, ProfileView, LogoutView, ForgotPasswordView, PasswordResetView

app_name = 'Authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user-check/', UserCheckView.as_view(), name='user-check'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Password reset endpoints
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
]
