from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from .models import Customer
from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    # Define a regular expression pattern to match phone numbers with country code
    pattern = r'^\+\d{1,3}\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('Please enter a phone number with country code, e.g. +91xxxxxxxxxx')

class CustomerRegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True, help_text='Phone number', validators=[validate_phone_number])

    class Meta:
        model = Customer
        fields = ['email', 'phone', 'first_name', 'last_name', 'password1', 'password2']
        widget = {
            'email' : forms.EmailInput(attrs={'class': 'form-control'}),
            'phone' : forms.TextInput(attrs={'class': 'form-control'}),
            'first_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'last_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'password1' : forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2' : forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='Enter code')

class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=(forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Old Password'})))
    new_password1 = forms.CharField(max_length=20, widget=(forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'New Password'})))
    new_password2 = forms.CharField(max_length=20, widget=(forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Confirm New Password'})))

    class Meta:
        model = Customer
        fields = ['old_password', 'new_password1', 'new_password2']

class EditUserProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Enter email'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter phone number.'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter first name.'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter last name.'}))

    class Meta:
        model = Customer
        fields = ['email', 'phone', 'first_name', 'last_name']
