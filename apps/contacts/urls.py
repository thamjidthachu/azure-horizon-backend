from django.urls import path
from .views import ContactMessageView


app_name = 'contacts'
urlpatterns = [
    path('new/', ContactMessageView.as_view(), name='contact-message'),
]
