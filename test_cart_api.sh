#!/bin/bash

# Cart API Testing Script
# This script demonstrates the cart and order functionality

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api"

echo "=== Cart and Order Management API Test ==="
echo "Make sure the Django server is running on $BASE_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_header=$4
    
    echo -e "${YELLOW}$method $endpoint${NC}"
    if [ -n "$data" ]; then
        echo "Data: $data"
    fi
    
    if [ -n "$auth_header" ]; then
        curl -s -X $method \
             -H "Content-Type: application/json" \
             -H "$auth_header" \
             -d "$data" \
             "$API_BASE$endpoint" | python -m json.tool 2>/dev/null || echo "Response not JSON"
    else
        curl -s -X $method \
             -H "Content-Type: application/json" \
             -d "$data" \
             "$API_BASE$endpoint" | python -m json.tool 2>/dev/null || echo "Response not JSON"
    fi
    echo ""
}

echo "=== Cart API Endpoints ==="
echo ""

echo "1. Health Check"
api_call "GET" "/../../healthz/"

echo "2. User Registration (for testing)"
USER_DATA='{"username":"testuser","email":"test@example.com","password":"testpass123","phone":"1234567890"}'
api_call "POST" "/auth/register/" "$USER_DATA"

echo "3. User Login"
LOGIN_DATA='{"email":"test@example.com","password":"testpass123"}'
LOGIN_RESPONSE=$(curl -s -X POST \
                     -H "Content-Type: application/json" \
                     -d "$LOGIN_DATA" \
                     "$API_BASE/auth/login/")
echo "$LOGIN_RESPONSE" | python -m json.tool 2>/dev/null

# Extract token from login response
TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)
AUTH_HEADER="Authorization: Bearer $TOKEN"

echo ""
echo "=== Cart Operations (Authenticated) ==="

echo "4. Get or Create Active Cart"
api_call "GET" "/cart/cart/active/" "" "$AUTH_HEADER"

echo "5. List Services (to get service IDs)"
api_call "GET" "/../../services/" "" "$AUTH_HEADER"

echo "6. Add Item to Cart (replace service_id with actual ID)"
CART_ITEM_DATA='{"service_id":1,"quantity":2,"booking_date":"2025-11-01","special_requests":"Test booking"}'
api_call "POST" "/cart/cart/add/" "$CART_ITEM_DATA" "$AUTH_HEADER"

echo "7. Get Active Cart with Items"
api_call "GET" "/cart/cart/active/" "" "$AUTH_HEADER"

echo "8. Update Cart Item (replace item_id with actual ID)"
UPDATE_DATA='{"quantity":3,"special_requests":"Updated booking request"}'
api_call "PUT" "/cart/cart/items/1/" "$UPDATE_DATA" "$AUTH_HEADER"

echo "9. Checkout Cart"
CHECKOUT_DATA='{"customer_name":"John Doe","customer_email":"john@example.com","customer_phone":"1234567890","special_instructions":"Please confirm booking"}'
api_call "POST" "/cart/cart/checkout/" "$CHECKOUT_DATA" "$AUTH_HEADER"

echo "10. List Orders"
api_call "GET" "/cart/orders/" "" "$AUTH_HEADER"

echo "11. Complete Payment (replace order_id with actual ID)"
api_call "POST" "/cart/orders/1/complete-payment/" "" "$AUTH_HEADER"

echo "12. Remove Item from Cart (replace item_id with actual ID)"
api_call "DELETE" "/cart/cart/items/1/remove/" "" "$AUTH_HEADER"

echo "13. Clear Cart"
api_call "DELETE" "/cart/cart/clear/" "" "$AUTH_HEADER"

echo ""
echo -e "${GREEN}=== Cart API Test Complete ===${NC}"
echo "Note: Replace placeholder IDs with actual IDs from your database"
echo "Some endpoints may fail if the referenced objects don't exist"