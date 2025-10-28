from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

# DRF router for cart item PATCH endpoint
router = DefaultRouter()
router.register(r'cart/items', views.CartItemViewSet, basename='cartitem')

urlpatterns = [
    # Cart URLs
    path('<int:pk>/detail/', views.CartDetailView.as_view(), name='cart-detail'),
    path('get-my-cart/', views.get_or_create_active_cart, name='active-cart'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('items/<int:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('clear-cart/', views.clear_cart, name='clear-cart'),
    # Checkout URLs
    path('checkout/', views.checkout_cart, name='checkout-cart'),
    # Order URLs
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/complete-payment/', views.complete_payment, name='complete-payment'),
    # DRF router endpoints
    path('', include(router.urls)),
]