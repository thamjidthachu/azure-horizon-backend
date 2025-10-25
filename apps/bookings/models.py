# Create your models here.
from django.db import models
from decimal import Decimal

from apps.authentication.models import User
from apps.service.models import Service
from apps.utils import ActiveModel, TimeStampedModel


class Booking(TimeStampedModel, ActiveModel):
    """Main booking model for resort service reservations"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    # Customer Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    guest_name = models.CharField(max_length=200, help_text="Full name of the guest")
    guest_email = models.EmailField(help_text="Contact email")
    guest_phone = models.CharField(max_length=20, help_text="Contact phone number")
    
    # Booking Details
    booking_number = models.CharField(max_length=50, unique=True, editable=False)
    booking_date = models.DateField(help_text="Date of the booking/reservation")
    booking_time = models.TimeField(null=True, blank=True, help_text="Time of the booking (if applicable)")
    number_of_guests = models.PositiveIntegerField(default=1)
    
    # Status and Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional Information
    special_requests = models.TextField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True, help_text="Internal notes for staff")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['booking_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Booking #{self.booking_number} - {self.guest_name}"
    
    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate unique booking number
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.booking_number = f"BK-{timestamp}-{unique_id}"
        
        # Calculate totals
        self.calculate_totals()
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from booking services"""
        booking_services = self.booking_services.all()
        self.subtotal = sum(bs.total_price for bs in booking_services)
        self.tax = self.subtotal * Decimal('0.05')  # 5% tax
        self.total_amount = self.subtotal + self.tax


class BookingService(TimeStampedModel):
    """Services included in a booking"""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1, help_text="Number of people/units")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.service.name} - {self.quantity} x ${self.unit_price}"
    
    def save(self, *args, **kwargs):
        # Set unit price from service if not provided
        if not self.unit_price:
            self.unit_price = self.service.price
        
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        
        # Update booking totals
        if self.booking_id:
            self.booking.calculate_totals()
            self.booking.save()


class Payment(TimeStampedModel):
    """Payment records for bookings"""
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.booking.booking_number} - ${self.amount}"
