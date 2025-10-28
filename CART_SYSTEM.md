# Cart and Order Management System

## Overview

The cart system allows users to add services to a shopping cart, manage cart items, and checkout to create orders. The cart remains persistent across user sessions and devices.

## Key Features

### 🛒 **Cart Management**
- **Persistent Cart**: Cart items remain intact when users login from other devices
- **Open Until Payment**: Cart stays open until payment is successfully completed
- **Automatic Totals**: Subtotal, tax (5%), and total amount calculated automatically
- **Guest Support**: Supports both authenticated users and guest sessions

### 📦 **Order Processing**
- **Order Creation**: Orders are created when users checkout their cart
- **Order Updates**: Orders can be updated if users checkout the same cart again
- **Payment Integration**: Cart closes only after successful payment completion
- **Order History**: Complete order history with detailed items

## Models

### 1. Cart
- **Status**: `open`, `closed`, `abandoned`
- **User Association**: Links to authenticated users or guest sessions
- **Automatic Calculations**: Subtotal, tax, and total amount
- **Expiration**: Optional cart expiration functionality

### 2. CartItem
- **Service Reference**: Links to service being ordered
- **Booking Details**: Date, time, special requests
- **Pricing**: Unit price and total price calculations
- **Quantity**: Number of units/people

### 3. OrderDetail
- **Order Tracking**: Unique order number generation
- **Customer Info**: Name, email, phone (captured at checkout)
- **Status Tracking**: `pending`, `processing`, `confirmed`, `completed`, `cancelled`
- **Payment Status**: `unpaid`, `partial`, `paid`, `refunded`

### 4. OrderItem
- **Order Contents**: Snapshot of cart items at checkout time
- **Service Details**: Preserved service information
- **Booking Info**: Date, time, special requests

## API Endpoints

### Cart Operations
```
GET    /api/cart/cart/active/                 # Get or create active cart
POST   /api/cart/cart/add/                    # Add item to cart
PUT    /api/cart/cart/items/{id}/             # Update cart item
DELETE /api/cart/cart/items/{id}/remove/      # Remove item from cart
DELETE /api/cart/cart/clear/                  # Clear entire cart
```

### Checkout & Orders
```
POST   /api/cart/cart/checkout/               # Checkout cart (create order)
GET    /api/cart/orders/                      # List user orders
GET    /api/cart/orders/{id}/                 # Get order details
POST   /api/cart/orders/{id}/complete-payment/ # Mark payment as completed
```

## Usage Flow

### 1. Adding Items to Cart
```json
POST /api/cart/cart/add/
{
    "service_id": 1,
    "quantity": 2,
    "booking_date": "2025-11-01",
    "booking_time": "10:00:00",
    "special_requests": "Window seat preferred"
}
```

### 2. Checkout Process
```json
POST /api/cart/cart/checkout/
{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "1234567890",
    "special_instructions": "Please confirm 24 hours before"
}
```

### 3. Complete Payment
```json
POST /api/cart/orders/{order_id}/complete-payment/
```

## Key Business Logic

### Cart Persistence
- Cart items are saved to database immediately
- Users can access same cart from multiple devices
- Cart survives browser sessions and app restarts

### Order Lifecycle
1. **Cart Creation**: User adds items to cart
2. **Checkout**: Order is created from cart items
3. **Payment Processing**: External payment processing
4. **Payment Completion**: Cart is closed, order marked as paid
5. **Fulfillment**: Services are delivered

### Automatic Calculations
- **Unit Price**: Taken from service at time of adding to cart
- **Total Price**: Unit price × quantity
- **Subtotal**: Sum of all item total prices
- **Tax**: 5% of subtotal
- **Total Amount**: Subtotal + tax

## Admin Interface

All models are registered in Django admin with:
- **Filtering**: By status, dates, users
- **Search**: By names, emails, order numbers
- **Inline Editing**: Cart items in cart view, order items in order view
- **Read-only Fields**: Calculated fields like totals and timestamps

## Testing

Use the included `test_cart_api.sh` script to test all cart functionality:

```bash
./test_cart_api.sh
```

## Database Indexes

Optimized indexes for:
- User cart lookups
- Order history queries
- Status-based filtering
- Date-based sorting

## Future Enhancements

- **Cart Abandonment**: Automatic cart cleanup after expiration
- **Inventory Management**: Stock checking before adding to cart
- **Promotional Codes**: Discount and coupon system
- **Wishlist**: Save items for later functionality
- **Multi-currency**: Support for different currencies