from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserCheckView, RegisterView, LoginView, ProfileView, HealthCheckView

app_name = 'Authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user-check/', UserCheckView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
