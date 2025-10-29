from django.db import models

class PaymentStatusChoices(models.TextChoices):
    INITIATED = 'initiated', 'Initiated'
    WAITING_FOR_CONFIRMATION = 'waiting_for_confirmation', 'Waiting for Confirmation'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class PaymentMethodChoices(models.TextChoices):
    CASH = 'cash', 'Cash'
    CREDIT_CARD = 'credit_card', 'Credit Card'
    DEBIT_CARD = 'debit_card', 'Debit Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    ONLINE = 'online', 'Online Payment'


class BookingStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class GenderChoices(models.TextChoices):
    FEMALE = 'F', 'Female'
    MALE = 'M', 'Male'

class CartStatusChoices(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'
    ABANDONED = 'abandoned', 'Abandoned'

class OrderStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'