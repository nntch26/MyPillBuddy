from django.contrib import admin
from .models import *

# Register your models here.

# Register your models here.
admin.site.register(Medication)
admin.site.register(Doctor)
admin.site.register(Prescription)
admin.site.register(MedicationReminder)