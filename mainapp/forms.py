from django import forms

from .models import Order

class Registration(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.IntegerField()
    address = forms.CharField()


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ['cart', 'status', 'user']
