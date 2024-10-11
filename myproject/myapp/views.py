from django.shortcuts import render, redirect
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm
from .models import *

class indexView(View):
    def get(self, request):
        return render(request, 'index.html')

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            patient = form.save()
            Patient.objects.create(
                user = patient,
                phone_number = form.cleaned_data["phone_number"],
                birth_date = form.cleaned_data["birth_date"],
                address = form.cleaned_data["address"],
                gender = form.cleaned_data["gender"],
                health_detail = form.cleaned_data["health_detail"],
                chronic_disease = form.cleaned_data["chronic_disease"]
            )
            login(request,patient)
            return redirect('home')
        
        return render(request, 'register.html', {'form': form})
    
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('home')
        return render(request, 'login.html', {'form': form})
    


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('url_login')

class ProfileView(View):
    def get(self, request):
        patient = Patient.objects.get(id=request.user.id)
        box = {'patient': patient}
        return render(request, 'profile.html', box)

class HistoryView(View):
    def get(self, request):
        return render(request, 'history.html')

class MedicationView(View):
    def get(self, request):
        return render(request, 'medication.html')


# Doctor
class ShowMedicationView(View):
    def get(self, request):
        return render(request, 'temp_doctor/show_medication.html')
    
class AddMedicationView(View):
    def get(self, request):
        return render(request, 'temp_doctor/add_medication.html')

class DoctorView(View):
    def get(self, request):
        return render(request, 'temp_doctor/doctor.html')
    


class PatientListView(View):
    def get(self, request):
        patient_list = User.objects.exclude(
            Q(username__startswith='admin') | 
            Q(username__startswith='doctor') ) 
        # ไม่เอา admin staff doctor

        return render(request, 'temp_doctor/patient_list.html', {'patient_list':patient_list})

class PatientDelView(View):

    def get(self, request, patient_id):
        patient_data = User.objects.get(pk=patient_id)
        patient_data.delete()
        return redirect('url_patientlist')
    

class PatientAddView(View):
    def get(self, request):
        return render(request, 'temp_doctor/patient_list.html')