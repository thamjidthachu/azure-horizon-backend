from django import forms
from .models import CartItem, OrderDetail


class AddToCartForm(forms.ModelForm):
    """Form for adding items to cart"""
    
    class Meta:
        model = CartItem
        fields = ['service', 'quantity', 'booking_date', 'booking_time', 'special_requests']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        return quantity


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""
    
    class Meta:
        model = OrderDetail
        fields = ['customer_name', 'customer_email', 'customer_phone', 'special_instructions']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'special_instructions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email')
        if email:
            # Add any custom email validation here
            pass
        return email


class UpdateCartItemForm(forms.ModelForm):
    """Form for updating cart items"""
    
    class Meta:
        model = CartItem
        fields = ['quantity', 'booking_date', 'booking_time', 'special_requests']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        return quantity