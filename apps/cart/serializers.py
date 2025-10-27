from rest_framework import serializers
from .models import Cart, CartItem, OrderDetail, OrderItem
from apps.service.serializers import ServiceListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceListSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'service', 'service_id', 'quantity', 'unit_price', 'total_price',
            'booking_date', 'booking_time', 'special_requests', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']

    def validate_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value



# --- FLAT CART SERIALIZER ---
class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_id', 'status', 'subtotal', 'tax', 'total_amount',
            'total', 'items', 'items_count', 'expires_at', 'last_activity', 'created_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'tax', 'total_amount', 'total', 'last_activity', 'created_at'
        ]

    def get_total(self, obj):
        return str(obj.total_amount)

    def get_items(self, obj):
        items = []
        for cart_item in obj.cart_items.filter(is_active=True):
            service = cart_item.service
            service_image = ''
            # Try to get the first image from service.files (FileSerializer)
            if service and hasattr(service, 'file_set'):
                file_qs = service.file_set.all()
                if file_qs.exists():
                    file_obj = file_qs.first()
                    if hasattr(file_obj, 'images') and file_obj.images:
                        service_image = str(file_obj.images.url)
            item = {
                'id': cart_item.id,
                'service_id': service.id if service else None,
                'service_name': getattr(service, 'name', None),
                'service_price': str(getattr(service, 'price', '')),
                'quantity': cart_item.quantity,
                'booking_date': cart_item.booking_date,
                'booking_time': cart_item.booking_time,
                'subtotal': str(cart_item.total_price),
                'service_slug': getattr(service, 'slug', None),
                'service_image': service_image,
                'service_duration': getattr(service, 'time', None),
                'service_description': getattr(service, 'synopsis', None),
                'unit': getattr(service, 'unit', None),
                'rating': getattr(service, 'rating', None) if hasattr(service, 'rating') else None,
                'review_count': getattr(service, 'review_count', None) if hasattr(service, 'review_count') else None,
                'special_requests': cart_item.special_requests,
                'is_active': cart_item.is_active,
                'created_at': cart_item.created_at,
            }
            items.append(item)
        return items

    def get_items_count(self, obj):
        return obj.get_items_count()


class AddToCartSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    booking_date = serializers.DateField(required=False)
    booking_time = serializers.TimeField(required=False)
    special_requests = serializers.CharField(max_length=500, required=False)
    
    def validate_service_id(self, value):
        from apps.service.models import Service
        try:
            Service.objects.get(id=value, is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity', 'booking_date', 'booking_time', 'special_requests']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'service', 'quantity', 'unit_price', 'total_price',
            'booking_date', 'booking_time', 'special_requests', 'status'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderDetail
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'customer_email', 'customer_phone',
            'status', 'payment_status', 'subtotal', 'tax', 'total_amount',
            'order_date', 'checkout_date', 'fulfillment_date',
            'special_instructions', 'order_items'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax', 'total_amount',
            'order_date', 'checkout_date'
        ]


class CheckoutSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=200)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)
    special_instructions = serializers.CharField(max_length=1000, required=False)
    
    def validate(self, data):
        # Additional validation can be added here
        return data