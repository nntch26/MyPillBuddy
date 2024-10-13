from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm, AddMedicationForm, PrescriptionForm,MedicationReminderForm
from .models import *
from django.contrib.auth.models import Group

from django.http import HttpResponse
from gtts import gTTS
import os
from datetime import datetime, timedelta
import time
from django.conf import settings


class indexView(View):
    def get(self, request):
        return render(request, 'index.html')

class HomeView(View):
    def get(self, request):
        current_date = datetime.now()
        take = request.GET.get('click', None)
        current_time_plus_five = (datetime.now() + timedelta(minutes=5)).time()

        if take:
            medi = MedicationReminder.objects.get(id=take)
            medi.taken = True
            medi.save()

        patients = request.user
        print(patients)  

        remimder_late = MedicationReminder.objects.filter(
            prescription__patient__id= patients.id,
            taken = False,
            reminder_time__lt=current_date.time()
        ).order_by('reminder_time')
         # ดึงรายการยาที่ต้องกินตามเวลาปัจจุบัน เรียงตามเวลาที่ต้องกิน
        reminder_list = MedicationReminder.objects.filter(
            prescription__patient__id= patients.id,
            reminder_time__gte=current_time_plus_five  
        ).order_by('reminder_time', 'taken')  

        print(reminder_list)
        print(remimder_late)


        context = {
            'current_date':current_date,
            'reminder_list':reminder_list,
            'remimder_late':remimder_late
        }
        return render(request, 'home.html', context)

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
        user1 = User.objects.get(id=request.user.id)
        print(user1)
        box = {'user1': user1}
        return render(request, 'profile.html', box)


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

        # ส่งข้อมูล form และข้อมูลยาไปยัง template (แต่ในกรณีนี้ส่วนใหญ่ไม่จำเป็น)
        context = {"form": form, "medication": medication}
        return render(request, 'temp_doctor/show_medication.html', context)





#//////////////////// หน้าหลักของหมอ ///////////////////

class DoctorView(View):
    def get(self, request):
        doctor = get_object_or_404(Doctor, user=request.user) # หมอที่ล็อกอินอยู่
        patient_list = User.objects.filter(patient__doctor=doctor) # แสดงเฉพาะคนไข้ของหมอที่ล๊อคอินอยู่

        prescription_list = Prescription.objects.filter(doctor=doctor).order_by("-id")[0:4]
        print(prescription_list)

        medication_list = Medication.objects.all().order_by("-id")[0:6]


        context = {
            'prescription_list':prescription_list,
            'patient_list':patient_list,
            'medication_list':medication_list
        }


        return render(request, 'temp_doctor/doctor.html', context)
    

#//////////////////// ใบสั่งยา ///////////////////


class PrescriptionView(View):

    def get(self, request, patient_id):
        
        patient_select = User.objects.get(pk=patient_id)
       
        form = PrescriptionForm()
        context = {
            'form':form, 
            'patient_select':patient_select,
        }
        
        return render(request, 'temp_doctor/prescription.html', context)


    def post(self, request, patient_id):
        
        doctor1 = get_object_or_404(Doctor, user=request.user)# หมอที่ล็อกอินอยู่
        patient1 = get_object_or_404(User, id=patient_id) # หา id คนไข้

        form = PrescriptionForm(request.POST)
        print(form)
        print(form.errors)
        
        if form.is_valid():
            form.instance.patient = patient1
            form.instance.doctor = doctor1
            prescription = form.save()  

            # ส่งใบสั่งยาเมื้อกี้ที่สร้าง ไปหน้าตั้งเวลา
            return redirect('url_addreminder', id= prescription.id)


        patient_select = User.objects.get(pk=patient_id)
        form = PrescriptionForm()

        context = {
            'form':form, 
            'patient_select':patient_select
        }
        return render(request, 'temp_doctor/prescription.html', context)
    
class PrescriptionListView(View):
    def get(self, request, patient_id):
        prescription_list = Prescription.objects.filter(patient__id=patient_id)
        print(prescription_list)

        context = {
            'prescription_list':prescription_list,
        }

        return render(request, 'temp_doctor/prescription_list.html', context)


class DelPrescriptionView(View):
    
    def get(self, request, prescript_id):
        prescription_get = get_object_or_404(Prescription, pk=prescript_id)
        print(prescription_get)
        
        patient = prescription_get.patient # ดึง patient ออกมา

        prescription_get.delete() 
        # กลับไปและส่ง id ของ patient ไปด้วย
        return redirect('url_prescription_list', patient_id=patient.id)



#//////////////////// ตั้งเวลาแจ้งเตือน ///////////////////

class AddReminderView(View):

    def get(self, request, id):

        reminder_list = MedicationReminder.objects.filter(prescription__id=id)

        form = MedicationReminderForm()
        context = {
            'form':form, 
            'reminder_list':reminder_list,
            'id': id
        }
            
        return render(request, 'temp_doctor/reminder.html', context)


    def post(self, request, id):

        prescription1 = get_object_or_404(Prescription, pk=id)  # ดึง Prescription จาก id ที่ส่งมา
        print(prescription1)

        form = MedicationReminderForm(request.POST)
        print(form)
        print(form.errors)
        
        
        if form.is_valid():
            form.instance.prescription = prescription1
            form.save()
            return redirect('url_addreminder', id=id)


        reminder_list = MedicationReminder.objects.filter(prescription__id=id)

        form = MedicationReminderForm()
        context = {
            'form':form, 
            'reminder_list':reminder_list,
            'id': id
        }
        
        return render(request, 'temp_doctor/reminder.html', context)



class DelReminderView(View):

    def get(self, request, id):
        reminder_get = get_object_or_404(MedicationReminder, pk=id)
        print(reminder_get)
        
        prescription = reminder_get.prescription # ดึง prescription ออกมา

        reminder_get.delete() # ลบเวลานี้

        # กลับไป addreminder และส่ง id ของ prescription ไปด้วย
        return redirect('url_addreminder', id=prescription.id)

            

#//////////////////// รายชื่อคนไข้ ///////////////////

class PatientListView(View):
    def get(self, request):
        data = request.GET.get('search', None)


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

        doctor = get_object_or_404(Doctor, user=request.user) # หมอที่ล็อกอินอยู่
        patient_list = User.objects.filter(patient__doctor=doctor) # แสดงเฉพาะคนไข้ของหมอที่ล๊อคอินอยู่
        print(patient_list)

        context = {
            'patient_list':patient_list,
            'patient_all':patient_all,
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
        patient = get_object_or_404(Patient, user__id=patient_id) # หา id คนไข้

        # เพิ่มคนไข้ให้กับหมอ
        doctor.patients.add(patient)
        return redirect('url_patientlist')



class AlertNotificationView(View):
    def get(self, request, *args, **kwargs):
        target_time = "18:28:10"  # กำหนดเวลา (ไม่รวมวันที่)
        
        audio_folder = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'audio')
        
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        
        # วนลูปเช็คเวลาทุกๆ 1 วินาที
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")  # เอาแค่เวลา
            
            if current_time == target_time:
                # สร้างข้อความแจ้งเตือน
                alert_message = "ได้เวลาทานยาแล้ว"
                
                # สร้างเสียงแจ้งเตือน
                tts = gTTS(text=alert_message, lang='th')
                audio_file_path = os.path.join(audio_folder, "reminder.mp3")
                tts.save(audio_file_path)  # บันทึกไฟล์เสียงในโฟลเดอร์ที่กำหนด

                # ส่ง URL ของไฟล์เสียงไปยังหน้าเว็บ
                audio_url = '/static/audio/reminder.mp3'
                return render(request, 'alert_notification.html', {'audio_url': audio_url})

            # เช็คว่าเวลาผ่านไปแล้วหรือยัง
            if datetime.now().strftime("%H:%M:%S") > target_time:
                # ส่งข้อความว่า "เลยเวลาทานยาแล้ว"
                return HttpResponse("เลยเวลาทานยาแล้ว")
            
            # หน่วงเวลา 1 วินาที
            time.sleep(1)

