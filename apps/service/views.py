from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from resortproject import settings
from .models import Service, Comment
from .serializers import ServicesSerializer, CommentsSerializer, ServiceListSerializer

class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        services = Service.objects.order_by('-create_time')[:3]
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.order_by('-create_time')
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServicesSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

class ServiceReviewsView(generics.ListCreateAPIView):
    serializer_class = CommentsSerializer
    pagination_class = CustomPagination
    authentication_classes = []  # Disable session authentication for this view
    permission_classes = [permissions.AllowAny]  # Or set appropriate permissions

    def get_queryset(self):
        service = get_object_or_404(Service, slug=self.kwargs['service_slug'])
        return service.service_comment.all().order_by('-comment_time')

    def create(self, request, *args, **kwargs):
        # This bypasses CSRF for API requests
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        service = get_object_or_404(Service, slug=self.kwargs['service_slug'])
        # For unauthenticated users, you might want to handle this differently
        user = None
        if self.request.user.is_authenticated:
            user = self.request.user
        
        serializer.save(
            content_object=service,
            author=user,  # This will be None if user is not authenticated
            content_type=ContentType.objects.get_for_model(Service),
            object_id=service.id
        )


class ReviewReplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id, format=None):
        parent_comment = get_object_or_404(Comment, id=comment_id)
        service = parent_comment.content_object
        reply_text = request.data.get('reply')
        if not reply_text:
            return Response({'detail': 'Reply text required.'}, status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(User, user_id=request.user.id)
        timestamp = timezone.now()
        reply = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=parent_comment.id,
            message=reply_text,
            author=author,
            comment_time=timestamp
        )
        # Email notification
        users = parent_comment.author
        user_obj = get_object_or_404(User, id=users.id)
        email = user_obj.user.email
        subject = 'Resort Business'
        message = f'Hi {users}, {author} replied on your Comment "{parent_comment}" as "{reply_text}"'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        return Response({'detail': 'Reply posted.'}, status=status.HTTP_201_CREATED)
