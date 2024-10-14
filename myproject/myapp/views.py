from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.db.models import F, Q, Count, Value as V, Avg, Max, Min
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm, AddMedicationForm, PrescriptionForm,MedicationReminderForm
from .models import *
from django.contrib.auth.models import Group


from gtts import gTTS
import os
from datetime import datetime, timedelta
import time
from django.conf import settings
import pygame

from django.utils import timezone
import time
import datetime



class indexView(View):
    def get(self, request):
        return render(request, 'index.html')

class HomeView(View):

    def get(self, request):
        current_date = datetime.datetime.now()
        take = request.GET.get('click', None)

        # กดกินยาแล้ว
        if take:
            medi = MedicationReminder.objects.get(id=take)
            medi.taken = True
            medi.save()

            # ลบไฟล์ alert.mp3
            file_path = 'myapp/static/alert.mp3'
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print("ไฟล์ถูกลบเรียบร้อยแล้ว")
            else:
                print("ไม่พบไฟล์ที่ต้องการลบ")

        patients = request.user
        print(patients) 


        midnight = timezone.now().replace(hour=0, minute=0, second=0).time()
        
        # เที่ยงคืน อัปเดตสถานะ taken เป็น False สำหรับยา ที่ยังไม่หมดอายุ
        if midnight == timezone.now().time():
            MedicationReminder.objects.filter(
                prescription__end_date__gte=timezone.now().date(),
                taken=True
            ).update(taken=False)


        # แจ้งกินยาเลท (เวลาปัจจุบัน > reminder_time)
        reminder_late = MedicationReminder.objects.filter(
            prescription__patient__id=patients.id,
            taken=False,
            reminder_time__lt=current_date.time(),
            prescription__end_date__gte=current_date.date()  # ต้องยังไม่เกินวัน end_date
        ).order_by('reminder_time')


         # ดึงรายการยาที่ต้องกินตามเวลาปัจจุบัน เรียงตามเวลาที่ต้องกิน (เวลาปัจจุบัน <= reminder_time)
        reminder_list = MedicationReminder.objects.filter(
            prescription__patient__id=patients.id,
            taken=False,  # ต้องยังไม่ถูกกิน
            reminder_time__gte=current_date.time(),
            prescription__end_date__gte=current_date.date()
        ).order_by('reminder_time') 


        # แจ้งกินยาแล้ว
        reminder_eaten = MedicationReminder.objects.filter(
            prescription__patient__id=patients.id,
            taken=True,  # ถูกกินแล้ว
            prescription__end_date__gte=current_date.date()
        ).order_by('-reminder_time')


        print(reminder_list)
        print(reminder_late)
        print(reminder_eaten)

        message = " "
        formatted_notify_time = None

        for i in reminder_late:
            itime = i.reminder_time
            print(itime)

            if  len(reminder_late) != 0 :

                print("111111111")
                formatted_notify_time2 = datetime.datetime.now().time().strftime('%H:%M')
                message = f"""ตอนนี้เวลา {formatted_notify_time2} ได้เวลาทานยาแล้ว 
                ยาที่ต้องทานคือ {i.prescription.medication.name}   
                {i.prescription.notes} {i.prescription.duration}
                """
            
                # สร้างเสียงพูดแจ้งเตือน
                tts = gTTS(text=message, lang='th')
                savefile = 'myapp/static/alert.mp3'
                tts.save(savefile)
                
                notify_time = datetime.datetime.now()
                print(notify_time)
                formatted_notify_time = notify_time.strftime('%Y-%m-%dT%H:%M:%S')


        context = {
            'current_date':current_date,
            'reminder_list':reminder_list,
            'reminder_late':reminder_late,
            'reminder_eaten':reminder_eaten,
            'message': message, 
            'notify_time': formatted_notify_time
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




class NotifyAtTimeView(View):
    def get(self, request, *args, **kwargs):
        # ดึงข้อมูล reminder จาก MedicationReminder ที่ยังไม่ได้ถูกทำเครื่องหมายว่าได้รับยาแล้ว
        reminders = MedicationReminder.objects.filter(taken=False)  # ดึงข้อมูลที่ยังไม่ได้กินยา
        print(reminders)
        
        # ใช้ timezone.localtime เพื่อให้แน่ใจว่าเวลาเป็นเขตเวลาในท้องถิ่น
        current_time = timezone.localtime(timezone.now()).time().replace(microsecond=0)
        current_dt = datetime.datetime.combine(datetime.date.today(), current_time)

        notification_messages = []
        audio_folder = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'audio')

        # วนลูปตรวจสอบแต่ละ reminder
        for reminder in reminders:
            reminder_time = reminder.reminder_time

            # แปลง reminder_time เป็น datetime object
            reminder_dt = datetime.datetime.combine(datetime.date.today(), reminder_time)

            # ถ้าเวลาปัจจุบันตรงกับ reminder_time
            if current_dt == reminder_dt:
                message = f"ถึงเวลาทานยาแล้ว: {reminder.prescription.medication.name}"
                notification_messages.append(message)

                print(f"Reminder time from DB: {reminder_time}")
                print(f"Current time: {current_time}")

                # ตรวจสอบให้แน่ใจว่าโฟลเดอร์ audio มีอยู่แล้ว
                if not os.path.exists(audio_folder):
                    os.makedirs(audio_folder)

                audio_file = os.path.join(audio_folder, 'reminder.mp3')

                # ถ้ามีไฟล์แล้ว ให้ลบไฟล์เก่า
                if os.path.exists(audio_file):
                    os.remove(audio_file)

                # สร้างไฟล์เสียงสำหรับการแจ้งเตือนแต่ละครั้ง
                tts = gTTS(message, lang='th')
                tts.save(audio_file)

                # เริ่มต้น Pygame mixer
                pygame.mixer.init()

                # โหลดและเล่นไฟล์เสียง
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # รอจนกว่าเสียงจะเล่นจบ
                while pygame.mixer.music.get_busy():
                    time.sleep(1)

                # ปิด Pygame mixer เพื่อไม่ให้ไฟล์ถูกล็อก
                pygame.mixer.quit()

            # ถ้าเวลาปัจจุบันยังไม่ถึงเวลาทานยา
            elif current_dt < reminder_dt:
                message = f"ยังไม่ถึงเวลาทานยา: {reminder.prescription.medication.name}"
                notification_messages.append(message)

            # ถ้าเวลาปัจจุบันเลยเวลาไปแล้ว (เผื่อในกรณีที่ระบบมาช้ากว่าเวลาจริง)
            elif current_dt > reminder_dt:
                message = f"เลยเวลาทานยาแล้ว: {reminder.prescription.medication.name}"
                notification_messages.append(message)

        # ถ้ามีการแจ้งเตือน
        if notification_messages:
            context = {'notifications': notification_messages}
        else:
            context = {'notifications': ['ไม่มีการเตือนในขณะนี้']}

        # ส่งข้อมูลไปยัง template
        return render(request, 'notify.html', context)
