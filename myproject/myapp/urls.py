
from django.urls import path
from .views import *



urlpatterns = [
    path("", indexView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("register/", RegisterView.as_view(), name="url_register"),
    path("login/", LoginView.as_view(), name="url_login"),
    path("logout/", LogoutView.as_view(), name="url_logout"),
    path("profile/", ProfileView.as_view(), name="url_profile"),
    path("medication/", MedicationView.as_view(), name="url_medication"),

    # doctor
    path("doctor/", DoctorView.as_view(), name="url_doctor"),
    path("Prescription/<int:patient_id>/", PrescriptionView.as_view(), name="url_prescription"),
    path("Prescription/<int:patient_id>/add/", PrescriptionView.as_view(), name="url_addprescription"),

    path("Reminder/<int:id>/", AddReminderView.as_view(), name="url_addreminder"),
    path("Reminder/<int:id>/add", AddReminderView.as_view(), name="url_addreminder2"),
    path("Reminder/<int:id>/del", DelReminderView.as_view(), name="url_delreminder"),

    path("ShowMedication/", ShowMedicationView.as_view(), name="url_showmedication"),
    path("DeleteMedication/<int:id>/", DeleteMedicationView.as_view(), name="url_deletemedication"),
    path("EditMedication/<int:id>/", EditMedicationView.as_view(), name="url_editmedication"),


    path("patient_list/", PatientListView.as_view(), name="url_patientlist"),
    path("patient_list/add/<int:patient_id>", PatientAddView.as_view(), name="url_addpatient"),
    path("patient_list/del/<int:patient_id>", PatientDelView.as_view(), name="url_delpatient"),
    path("patient_list/seach/", PatientListView.as_view(), name="seach"),


]
