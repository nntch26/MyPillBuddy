from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from .models import *

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    phone_number = forms.CharField(max_length=10)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    health_detail = forms.CharField(widget=forms.Textarea)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name',
                   'email', 'phone_number', 'birth_date', 'health_detail', 'address')
        

        