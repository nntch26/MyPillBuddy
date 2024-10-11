from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from .models import *

class CustomUserCreationForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=True)
    # last_name = forms.CharField(max_length=30, required=True)
    # email = forms.EmailField(max_length=254)
    # phone_number = forms.CharField(max_length=10)
    # health_detail = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

        