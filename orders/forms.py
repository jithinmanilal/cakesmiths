from django import forms
from .models import Address, Order
from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    # Define a regular expression pattern to match phone numbers with country code
    pattern = r'^\+\d{1,3}\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('Please enter a phone number with country code, e.g. +91xxxxxxxxxx')



class AddressForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=True, help_text='Phone number', validators=[validate_phone_number])

    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'pin']

        widget = {
            'first_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'phone' : forms.TextInput(attrs={'class': 'form-control'}),
            'email' : forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1' : forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2' : forms.TextInput(attrs={'class': 'form-control'}),
            'city' : forms.TextInput(attrs={'class': 'form-control'}),
            'state' : forms.TextInput(attrs={'class': 'form-control'}),
            'pin' : forms.TextInput(attrs={'class': 'form-control'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

        widget = {
            'status' : forms.TextInput(attrs={'class': 'form-control'}),
        }