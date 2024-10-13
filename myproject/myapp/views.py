from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm, AddMedicationForm, PrescriptionForm
from .models import *
from django.contrib.auth.models import Group

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
            group = Group.objects.get(name='patient')
            patient.groups.add(group)
            
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

            #ดึงเอา group ของผู้ใช้คนนี้ อันนี้ผู้ใช้มีแค่คนละ group เดียว
            user_groups = user.groups.all()
            for group in user_groups:
                print(group.name)  

            # ผู้ใช้ตรงกับ group ไหน เด้งไปหน้านั้น
            if group.name == "doctor":
                login(request, user)
                return redirect('url_doctor')
            else:
                login(request, user)
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
        pre = Prescription.objects.filter(patient_id = request.user.id)
        box = {'pre': pre}
        return render(request, 'medication.html', box)


# Doctor
#//////////////////// จัดการยา ///////////////////
class ShowMedicationView(View):
    def get(self, request):
        medication = Medication.objects.all()
        form = AddMedicationForm()
        context = {"form":form, 'medication':medication}
        return render(request, 'temp_doctor/show_medication.html', context)
    
    # AddMedication
    def post(self, request):
        form = AddMedicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('url_showmedication')
        context = {'form':form}
        return  render(request, 'temp_doctor/show_medication.html', context)

class DeleteMedicationView(View):
    def get(self, request, id): 
        medication = Medication.objects.get(id=id)
        medication.delete()
        return redirect('url_showmedication')
    
class EditMedicationView(View):
    def post(self, request, id):
        medication = Medication.objects.get(id=id)
        form = AddMedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()  
            return redirect('url_showmedication')

        context = {"form": form, "medication": medication,}
        return render(request, 'temp_doctor/show_medication.html', context)




#//////////////////// หน้าหลัก ///////////////////

class DoctorView(View):
    def get(self, request):
        return render(request, 'temp_doctor/doctor.html')
    

#//////////////////// สั่งยา ///////////////////


class PrescriptionView(View):

    def get(self, request, patient_id):
        
        patient_select = User.objects.get(pk=patient_id)

        form = PrescriptionForm()
        context = {
            'form':form, 
            'patient_select':patient_select
        }
        
        return render(request, 'temp_doctor/prescription.html', context)


    def post(self, request, patient_id):
        
        doctor1 = get_object_or_404(Doctor, user=request.user)# หมอที่ล็อกอินอยู่
        patient1 = get_object_or_404(Patient, id=patient_id) # หา id คนไข้

        form = PrescriptionForm(request.POST)
        print(form)
        print(form.errors)
        
        if form.is_valid():
            form.instance.patient = patient1
            form.instance.doctor = doctor1
            form.save()  
            return redirect('url_patientlist')


        patient_select = User.objects.get(pk=patient_id)
        form = PrescriptionForm()

        context = {
            'form':form, 
            'patient_select':patient_select
        }
        return render(request, 'temp_doctor/prescription.html', context)
    


#//////////////////// รายชื่อคนไข้ ///////////////////

class PatientListView(View):
    def get(self, request):
        data = request.GET.get('search', '')

        if data:
            # ค้นหาคนไข้จาก ID หรืออื่นๆ
            patient_all = User.objects.filter(pk = data)
        else:
            patient_all = User.objects.exclude(
            Q(username__startswith='admin') | 
            Q(username__startswith='doctor')|
            Q(patient__doctor__isnull=False)
            ) 
            # ไม่เอา admin staff doctor

        doctor = get_object_or_404(Doctor, user=request.user)# หมอที่ล็อกอินอยู่
        patient_list = Patient.objects.filter(doctor=doctor)

        # แสดงเฉพาะคนไข้ของหมอที่ล๊อคอินอยู่
        print(patient_list)

        context = {
            'patient_list':patient_list,
            'patient_all':patient_all
        }

        return render(request, 'temp_doctor/patient_list.html', context)
    

class PatientDelView(View):

    def get(self, request, patient_id):
        patient_data = User.objects.get(pk=patient_id)
        patient_data.delete()
        return redirect('url_patientlist')
    

class PatientAddView(View):
    def get(self, request, patient_id):
        
        doctor = get_object_or_404(Doctor, user=request.user)# หมอที่ล็อกอินอยู่
        patient_list = Patient.objects.filter(doctor=doctor)
        form = PrescriptionForm()

        # เพิ่มคนไข้ให้กับหมอ
        doctor.patients.add(patient)
        return redirect('url_patientlist')


class ReminderView(View):
    def get(self, request):
        return render(request,  'temp_doctor/reminder.html')
    


