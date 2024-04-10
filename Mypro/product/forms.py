from django import forms
from .models import Product, Rating, OrderStatus


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'image', 'category', 'available_quantity']


PAYMENT_METHOD_CHOICES = [
    ('credit_card', 'Credit Card'),
    ('paypal', 'PayPal'),
    ('google_pay', 'Google Pay'),
    ('cash_on_delivery', 'Cash on Delivery'),
]


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(max_length=255)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)  # Use ChoiceField for selecting payment method

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review'] 

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ['status']