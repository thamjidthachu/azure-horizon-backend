"""Resort_Business_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from apps.authentication.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include("django.contrib.auth.urls")),  # Django's built-in auth
    path('api/auth/', include('apps.authentication.urls')),  # API authentication endpoints
    path('services/', include('apps.service.urls')),
    path('healthz/', HealthCheckView.as_view(), name='healthz'),  # Add trailing slash
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
