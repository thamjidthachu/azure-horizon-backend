from django.urls import path
from .views import (
    CartDetailView, ActiveCartView, AddToCartView, UpdateCartItemView, CartItemRemoveView, ClearCartView,
    CheckoutCartView, OrderListView, OrderDetailView, CompletePaymentView
)

app_name = 'cart'


urlpatterns = [
    # Cart URLs
    path('<int:pk>/detail/', CartDetailView.as_view(), name='cart-detail'),
    path('get-my-cart/', ActiveCartView.as_view(), name='active-cart'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('items/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('items/<int:item_id>/remove/', CartItemRemoveView.as_view(), name='remove-from-cart'),
    path('clear-cart/', ClearCartView.as_view(), name='clear-cart'),
    # Checkout URLs
    path('checkout/', CheckoutCartView.as_view(), name='checkout-cart'),
    # Order URLs
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/complete-payment/', CompletePaymentView.as_view(), name='complete-payment'),
]