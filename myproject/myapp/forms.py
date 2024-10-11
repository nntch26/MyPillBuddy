from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from .models import *


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='ชื่อ')
    last_name = forms.CharField(max_length=30, label='นามสกุล')
    phone_number = forms.CharField(max_length=10, label='หมายเลขโทรศัพท์')
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='วันเกิด')
    health_detail = forms.CharField(widget=forms.Textarea, label='ข้อมูลสุขภาพ')
    address = forms.CharField(widget=forms.Textarea, label='ที่อยู่')
    chronic_disease = forms.CharField(max_length=255, label='โรคประจำตัว')

    GENDER_CHOICES = [
        ('', 'เลือกเพศ'),
        ('male', 'ชาย'),
        ('female', 'หญิง'),
        ('othor', 'ไม่ระบุ'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='เพศ')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 
                  'first_name', 'last_name', 'phone_number', 'birth_date', 
                  'health_detail', 'address', 'gender', 
                  'chronic_disease')

        labels = {
            'username': 'ชื่อผู้ใช้',
            'password1': 'รหัสผ่าน',
            'password2': 'ยืนยันรหัสผ่าน',
        }
