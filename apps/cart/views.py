
# --- CartItemViewSet for PATCH ---
from .models import CartItem  # Ensure CartItem is imported before use
from .serializers import CartItemSerializer  # Import serializer before use
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

class CartItemViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only allow access to user's own cart items in open carts
        return CartItem.objects.filter(cart__user=self.request.user, cart__status='open', is_active=True)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

from .models import Cart, CartItem, OrderDetail, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, OrderDetailSerializer, CheckoutSerializer
)
from apps.service.models import Service


class CartListCreateView(generics.ListCreateAPIView):
    """List user's carts or create a new cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_active=True)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_or_create_active_cart(request):
    """Get user's active cart or create one if none exists"""
    try:
        cart = Cart.objects.get(user=request.user, status='open', is_active=True)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user, status='open')
    
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add an item to the user's active cart"""
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        # Get or create active cart
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='open',
            is_active=True,
            defaults={'user': request.user}
        )
        
        # Get the service
        service = get_object_or_404(Service, id=serializer.validated_data['service_id'], is_active=True)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            service=service,
            booking_date=serializer.validated_data.get('booking_date'),
            booking_time=serializer.validated_data.get('booking_time'),
            defaults={
                'quantity': serializer.validated_data['quantity'],
                'unit_price': service.price,
                'special_requests': serializer.validated_data.get('special_requests', '')
            }
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
        
        # Update cart totals
        cart.calculate_totals()
        cart.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update a cart item"""
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
        cart__status='open',
        is_active=True
    )
    
    serializer = UpdateCartItemSerializer(cart_item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Update cart totals
        cart_item.cart.calculate_totals()
        cart_item.cart.save()
        
        return Response(CartItemSerializer(cart_item).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove an item from cart"""
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
        cart__status='open',
        is_active=True
    )
    
    cart = cart_item.cart
    cart_item.delete()
    
    # Update cart totals
    cart.calculate_totals()
    cart.save()
    
    return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from user's active cart"""
    try:
        cart = Cart.objects.get(user=request.user, status='open', is_active=True)
        cart.cart_items.filter(is_active=True).delete()
        # Update cart totals
        cart.calculate_totals()
        cart.save()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_cart(request):
    """Checkout cart and create order"""
    try:
        cart = Cart.objects.get(user=request.user, status='open', is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)
    
    if cart.is_empty():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CheckoutSerializer(data=request.data)
    if serializer.is_valid():
        # Create order
        order = OrderDetail.objects.create(
            user=request.user,
            cart=cart,
            customer_name=serializer.validated_data['customer_name'],
            customer_email=serializer.validated_data['customer_email'],
            customer_phone=serializer.validated_data['customer_phone'],
            special_instructions=serializer.validated_data.get('special_instructions', ''),
            subtotal=cart.subtotal,
            tax=cart.tax,
            total_amount=cart.total_amount,
            checkout_date=timezone.now()
        )

        # Create order items from cart items
        cart_items = cart.cart_items.filter(is_active=True)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                service=cart_item.service,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                booking_date=cart_item.booking_date,
                booking_time=cart_item.booking_time,
                special_requests=cart_item.special_requests
            )

        # --- Create or reuse Booking and Payment records ---
        from apps.bookings.models import Booking, BookingService, Payment
        # Try to find an existing booking for this user/cart/session that is not paid/cancelled
        booking = Booking.objects.filter(
            user=request.user,
            guest_email=serializer.validated_data['customer_email'],
            status__in=['pending', 'confirmed', 'in_progress'],
            payment_status__in=['unpaid', 'partial']
        ).order_by('-created_at').first()

        if booking:
            # Update booking details
            booking.guest_name = serializer.validated_data['customer_name']
            booking.guest_phone = serializer.validated_data['customer_phone']
            booking.booking_date = cart_items.first().booking_date if cart_items.exists() else timezone.now().date()
            booking.booking_time = cart_items.first().booking_time if cart_items.exists() else None
            booking.number_of_guests = cart.get_items_count()
            booking.subtotal = cart.subtotal
            booking.tax = cart.tax
            booking.total_amount = cart.total_amount
            booking.special_requests = serializer.validated_data.get('special_instructions', '')
            booking.save()
            # Remove old BookingService records and recreate from cart
            booking.booking_services.all().delete()
        else:
            booking = Booking(
                user=request.user,
                guest_name=serializer.validated_data['customer_name'],
                guest_email=serializer.validated_data['customer_email'],
                guest_phone=serializer.validated_data['customer_phone'],
                booking_date=cart_items.first().booking_date if cart_items.exists() else timezone.now().date(),
                booking_time=cart_items.first().booking_time if cart_items.exists() else None,
                number_of_guests=cart.get_items_count(),
                status='pending',
                payment_status='unpaid',
                subtotal=cart.subtotal,
                tax=cart.tax,
                total_amount=cart.total_amount,
                special_requests=serializer.validated_data.get('special_instructions', '')
            )
            booking.save()

        for cart_item in cart_items:
            BookingService.objects.create(
                booking=booking,
                service=cart_item.service,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                notes=cart_item.special_requests
            )

        # Now update totals after all BookingService records are created
        booking.calculate_totals()
        booking.save()

        # Try to find an existing pending payment for this booking
        payment = Payment.objects.filter(
            booking=booking,
            payment_status='pending',
            payment_method='online'
        ).order_by('-payment_date').first()
        if payment:
            payment.amount = cart.total_amount
            payment.notes = 'Stripe payment initiated from cart checkout.'
            payment.save()
        else:
            payment = Payment.objects.create(
                booking=booking,
                amount=cart.total_amount,
                payment_method='online',
                payment_status='pending',
                notes='Stripe payment initiated from cart checkout.'
            )

        # --- Initiate Stripe checkout ---
        from apps.bookings.stripe_utils import create_checkout_session
        stripe_result = create_checkout_session(booking)
        if stripe_result['success']:
            # Save the Stripe session_id to the Payment record (dedicated field)
            payment.session_id = stripe_result['session_id']
            payment.save(update_fields=['session_id'])
            return Response({
                'order': OrderDetailSerializer(order).data,
                'booking_number': booking.booking_number,
                'payment_id': payment.id,
                'stripe_checkout_url': stripe_result['checkout_url'],
                'stripe_session_id': stripe_result['session_id'],
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to create Stripe checkout session', 'details': stripe_result.get('error')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    """List user's orders"""
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OrderDetail.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OrderDetail.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_payment(request, order_id):
    """Mark order as completed and close cart after successful payment"""
    order = get_object_or_404(OrderDetail, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return Response({'error': 'Order already paid'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark order as completed
    order.mark_as_completed()
    order.fulfillment_date = timezone.now()
    order.save()
    
    return Response({
        'message': 'Payment completed successfully',
        'order_number': order.order_number
    }, status=status.HTTP_200_OK)
