from django import forms
from .models import Coupon

class CouponForm(forms.Form):
    code = forms.CharField()

    class Meta:
        model = Coupon
        fields = ['code']

        widget = {
            'code' : forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddCouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = ['code', 'valid_from', 'valid_till', 'discount', 'active']
        widget = {
            'code' : forms.TextInput(attrs={'class': 'form-control'}),
            'valid_from' : forms.DateTimeInput(attrs={'class': 'form-control'}),
            'valid_till' : forms.DateTimeInput(attrs={'class': 'form-control'}),
            'discount' : forms.NumberInput(attrs={'class': 'form-control'}),
            'active' : forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
