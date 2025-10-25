from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from rest_framework import status, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
import json

from .models import Booking, Payment
from .serializers import (
    BookingListSerializer, BookingDetailSerializer, 
    BookingCreateSerializer, PaymentSerializer
)
from .stripe_utils import (
    create_checkout_session, retrieve_checkout_session,
    verify_webhook_signature, handle_checkout_session_completed
)


class BookingPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking (public or authenticated)"""
    permission_classes = [AllowAny]
    serializer_class = BookingCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            booking = serializer.save()
            detail_serializer = BookingDetailSerializer(booking)
            
            return Response({
                "message": "Your booking has been created successfully! A confirmation email has been sent.",
                "booking": detail_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "error": "Something went wrong. Please check your booking details and try again.",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BookingListView(generics.ListAPIView):
    """List all bookings for authenticated user"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingListSerializer
    pagination_class = BookingPagination
    
    def get_queryset(self):
        user = self.request.user
        # Return bookings for authenticated user
        return Booking.objects.filter(user=user).order_by('-created_at')


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details by booking number"""
    permission_classes = [AllowAny]
    serializer_class = BookingDetailSerializer
    lookup_field = 'booking_number'
    
    def get_queryset(self):
        # If user is authenticated, show only their bookings
        # If not, allow access with booking number (for guests)
        if self.request.user.is_authenticated:
            return Booking.objects.filter(user=self.request.user)
        return Booking.objects.all()


class BookingUpdateStatusView(APIView):
    """Update booking status (admin only)"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, booking_number):
        # Check if user is staff
        if not request.user.is_staff:
            return Response({
                "error": "You don't have permission to update booking status"
            }, status=status.HTTP_403_FORBIDDEN)
        
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes')
        
        if new_status and new_status in dict(Booking.STATUS_CHOICES).keys():
            booking.status = new_status
        
        if admin_notes:
            booking.admin_notes = admin_notes
        
        booking.save()
        
        serializer = BookingDetailSerializer(booking)
        return Response({
            "message": "Booking status updated successfully",
            "booking": serializer.data
        }, status=status.HTTP_200_OK)


class BookingCancelView(APIView):
    """Cancel a booking"""
    permission_classes = [AllowAny]
    
    def post(self, request, booking_number):
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        # Check if user owns the booking or is staff
        if request.user.is_authenticated:
            if booking.user != request.user and not request.user.is_staff:
                return Response({
                    "error": "You don't have permission to cancel this booking"
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            # For guest bookings, verify email
            guest_email = request.data.get('email')
            if booking.guest_email != guest_email:
                return Response({
                    "error": "Invalid email for this booking"
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if booking can be cancelled
        if booking.status in ['completed', 'cancelled']:
            return Response({
                "error": f"Cannot cancel a booking that is already {booking.status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'cancelled'
        booking.save()
        
        return Response({
            "message": "Booking cancelled successfully",
            "booking_number": booking.booking_number
        }, status=status.HTTP_200_OK)


class PaymentCreateView(generics.CreateAPIView):
    """Create a payment for a booking (admin only)"""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def create(self, request, booking_number):
        if not request.user.is_staff:
            return Response({
                "error": "You don't have permission to create payments"
            }, status=status.HTTP_403_FORBIDDEN)
        
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(booking=booking)
            
            # Update booking payment status based on total paid
            total_paid = sum(p.amount for p in booking.payments.filter(payment_status='completed'))
            
            if total_paid >= booking.total_amount:
                booking.payment_status = 'paid'
            elif total_paid > 0:
                booking.payment_status = 'partial'
            
            booking.save()
            
            return Response({
                "message": "Payment recorded successfully",
                "payment": PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "error": "Invalid payment data",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MyBookingsView(generics.ListAPIView):
    """List all bookings for the authenticated user"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingListSerializer
    pagination_class = BookingPagination
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')


# ===== Stripe Payment Views =====

class CreateCheckoutSessionView(APIView):
    """Create a Stripe Checkout Session for a booking"""
    permission_classes = [AllowAny]
    
    def post(self, request, booking_number):
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        # Verify booking belongs to user (if authenticated) or email matches (for guests)
        if request.user.is_authenticated:
            if booking.user and booking.user != request.user and not request.user.is_staff:
                return Response({
                    "error": "You don't have permission to pay for this booking"
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            # For guest bookings, verify email
            guest_email = request.data.get('email')
            if booking.guest_email != guest_email:
                return Response({
                    "error": "Invalid email for this booking"
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if booking is already paid
        if booking.payment_status == 'paid':
            return Response({
                "error": "This booking has already been paid"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if booking is cancelled
        if booking.status == 'cancelled':
            return Response({
                "error": "Cannot pay for a cancelled booking"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Stripe checkout session
        result = create_checkout_session(booking)
        
        if result['success']:
            return Response({
                "message": "Checkout session created successfully",
                "session_id": result['session_id'],
                "checkout_url": result['checkout_url'],
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to create checkout session",
                "details": result.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(APIView):
    """Verify payment status from Stripe"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        session_id = request.query_params.get('session_id')
        booking_number = request.query_params.get('booking_number')
        
        if not session_id:
            return Response({
                "error": "session_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve session from Stripe
        session = retrieve_checkout_session(session_id)
        
        if not session:
            return Response({
                "error": "Invalid session"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get booking
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        return Response({
            "payment_status": session.payment_status,
            "booking_status": booking.status,
            "booking_payment_status": booking.payment_status,
            "amount_total": session.amount_total / 100,  # Convert from cents
            "customer_email": session.customer_email,
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            return HttpResponse("Missing signature", status=400)
        
        # Verify webhook signature
        event = verify_webhook_signature(payload, sig_header)
        
        if not event:
            return HttpResponse("Invalid signature", status=400)
        
        # Handle different event types
        event_type = event['type']
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            
            # Handle successful payment
            success = handle_checkout_session_completed(session)
            
            if success:
                return HttpResponse("Webhook handled successfully", status=200)
            else:
                return HttpResponse("Error processing webhook", status=500)
        
        elif event_type == 'payment_intent.succeeded':
            # Additional handling for payment intent succeeded
            payment_intent = event['data']['object']
            # Add custom logic here if needed
            return HttpResponse("Payment intent succeeded", status=200)
        
        elif event_type == 'payment_intent.payment_failed':
            # Handle payment failure
            payment_intent = event['data']['object']
            # Add custom logic for failed payments
            return HttpResponse("Payment failed", status=200)
        
        # Return success for unhandled event types
        return HttpResponse(f"Unhandled event type: {event_type}", status=200)


class BookingPaymentStatusView(APIView):
    """Get payment status for a booking"""
    permission_classes = [AllowAny]
    
    def get(self, request, booking_number):
        booking = get_object_or_404(Booking, booking_number=booking_number)
        
        # Calculate payment details
        total_paid = sum(
            p.amount for p in booking.payments.filter(payment_status='completed')
        )
        
        remaining = booking.total_amount - total_paid
        
        return Response({
            "booking_number": booking.booking_number,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "total_amount": str(booking.total_amount),
            "total_paid": str(total_paid),
            "remaining": str(remaining),
            "payments": PaymentSerializer(booking.payments.all(), many=True).data
        }, status=status.HTTP_200_OK)