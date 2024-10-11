from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    health_detail = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"       

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 

class Medication(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    medication = models.OneToOneField(Medication, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)  # เช่น 2 เม็ด
    frequency = models.CharField(max_length=100)  # เช่น วันละ 3 ครั้ง
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medication.name} - {self.patient.full_name}"

class MedicationReminder(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    taken = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.prescription.medication.name} at {self.reminder_time}"

    def is_past_due(self):
        return timezone.now() > self.reminder_time
