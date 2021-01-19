from django import forms
from django.contrib.auth.models import User

from .models import Order, GlobalCategory, Category


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError(f"User with username {username} don't exist")
        if not user.check_password(password):
            raise forms.ValidationError('Wrong password')
        return self.cleaned_data


class Registration(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.IntegerField()
    address = forms.CharField()

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is taken')
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not math')
        return self.cleaned_data


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ['cart', 'status', 'user']


class AddGCatForm(forms.ModelForm):

    class Meta:
        model = GlobalCategory
        fields = '__all__'

    def save(self):
        gcat_name = self.cleaned_data.get('name')
        GlobalCategory.objects.create(name=gcat_name)


class AddCatForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

    def save(self):
        to_cat = self.cleaned_data.get('global_category')
        name = self.cleaned_data.get('name')
        Category.objects.create(global_category=to_cat, name=name)

