from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserCheckView, RegisterView, LoginView, ProfileView, LogoutView

app_name = 'Authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user-check/', UserCheckView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
