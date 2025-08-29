from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.contacts.models import ContactMessage
from apps.contacts.serializers import ContactMessageSerializer

# Create your views here.


class ContactMessageView(ListCreateAPIView):
    permission_classes = []
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)

                # Send welcome email asynchronously using Celery
                send_email_message.delay(
                    subject="New Enquiry Received | Azure Horizon",
                    template_name="admin-enquiry-notification.html",
                    context=request.data,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL]
                )

                send_email_message.delay(
                    subject="Enquiry Received | Azure Horizon",
                    template_name="contact-response.html",
                    context=request.data,
                    recipient_list=[request.data.get('email')]
                )

                return Response(
                    {"message": "Your contact has been submitted successfully"}, 
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": "Something went wrong. Try again later"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            return Response(
                {"error": "Something went wrong. Try again later"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
