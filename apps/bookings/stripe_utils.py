"""
Stripe payment integration utilities for booking system
"""
import stripe
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET


def create_checkout_session(booking):
    """
    Create a Stripe Checkout Session for a booking
    
    Args:
        booking: Booking instance
        
    Returns:
        dict: Checkout session data with url and session_id
    """
    try:
        # Prepare line items from booking services
        line_items = []
        
        for item in booking.order.order_items.all():
            line_items.append({
                'price_data': {
                    'currency': 'aed',
                    'unit_amount': int(item.unit_price * 100),  # Convert to cents
                    'product_data': {
                        'name': item.service.name,
                        'description': f"{item.service.synopsis or 'Resort service'}",
                        'images': [],
                    },
                },
                'quantity': item.quantity,
            })
        
        # Add tax as a separate line item if applicable
        if booking.tax > 0:
            line_items.append({
                'price_data': {
                    'currency': 'aed',
                    'unit_amount': int(booking.tax * 100),
                    'product_data': {
                        'name': 'VAT (5%)',
                        'description': 'Value Added Tax (VAT)',
                    },
                },
                'quantity': 1,
            })
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=booking.order.customer_email,
            client_reference_id=booking.booking_number,
            metadata={
                'booking_number': booking.booking_number,
                'booking_id': str(booking.id),
                'guest_name': booking.order.customer_name,
            },
            success_url=f"{settings.PAYMENT_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}&booking_number={booking.booking_number}",
            cancel_url=f"{settings.PAYMENT_CANCEL_URL}?booking_number={booking.booking_number}",
        )
        
        logger.info(f"Stripe checkout session created for booking {booking.booking_number}: {checkout_session.id}")
        
        return {
            'success': True,
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url,
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session for booking {booking.booking_number}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session for booking {booking.booking_number}: {str(e)}")
        return {
            'success': False,
            'error': 'An unexpected error occurred',
        }


def retrieve_checkout_session(session_id):
    """
    Retrieve a Stripe Checkout Session
    
    Args:
        session_id: Stripe session ID
        
    Returns:
        stripe.checkout.Session or None
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving Stripe session {session_id}: {str(e)}")
        return None


def handle_checkout_session_completed(session):
    """
    Handle successful checkout session completion
    Updates booking and creates payment record
    
    Args:
        session: Stripe checkout session object
        
    Returns:
        bool: Success status
    """
    try:
        from .models import Booking, Payment
        
        booking_number = session.metadata.get('booking_number')
        
        if not booking_number:
            logger.error("No booking number in session metadata")
            return False
        
        booking = Booking.objects.filter(booking_number=booking_number).first()
        
        if not booking:
            logger.error(f"Booking {booking_number} not found")
            return False
        
        # Get payment intent to retrieve more details
        payment_intent_id = session.payment_intent
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=Decimal(session.amount_total / 100),  # Convert from cents
            payment_method='online',
            payment_status='completed',
            transaction_id=payment_intent_id,
            notes=f"Stripe payment - Session ID: {session.id}"
        )
        
        # Update booking payment status
        total_paid = sum(p.amount for p in booking.payments.filter(payment_status='completed'))
        
        if total_paid >= booking.total_amount:
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
        elif total_paid > 0:
            booking.payment_status = 'partial'
        
        booking.save()
        
        logger.info(f"Payment recorded for booking {booking_number}: ${payment.amount}")
        
        # Send payment confirmation email
        from utils import send_email_message
        
        send_email_message.delay(
            subject=f"Payment Confirmation | {booking.booking_number} | Azure Horizon",
            template_name="payment-confirmation.html",
            context={
                "booking_number": booking.booking_number,
                "guest_name": booking.order.customer_name,
                "amount": str(payment.amount),
                "transaction_id": payment_intent_id,
                "payment_method": "Credit/Debit Card",
                "booking_date": booking.booking_date.strftime('%B %d, %Y'),
            },
            recipient_list=[booking.guest_email]
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error handling checkout session completion: {str(e)}")
        return False


def create_refund(payment_intent_id, amount=None, reason='requested_by_customer'):
    """
    Create a refund for a payment
    
    Args:
        payment_intent_id: Stripe payment intent ID
        amount: Amount to refund in dollars (None for full refund)
        reason: Refund reason
        
    Returns:
        dict: Refund result
    """
    try:
        refund_params = {
            'payment_intent': payment_intent_id,
            'reason': reason,
        }
        
        if amount:
            refund_params['amount'] = int(amount * 100)  # Convert to cents
        
        refund = stripe.Refund.create(**refund_params)
        
        logger.info(f"Refund created for payment intent {payment_intent_id}: {refund.id}")
        
        return {
            'success': True,
            'refund_id': refund.id,
            'status': refund.status,
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating refund: {str(e)}")
        return {
            'success': False,
            'error': str(e),
        }


def verify_webhook_signature(payload, signature):
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Request body
        signature: Stripe signature header
        
    Returns:
        stripe.Event or None
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_SECRET
        )
        return event
    except ValueError:
        logger.error("Invalid webhook payload")
        return None
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        return None
