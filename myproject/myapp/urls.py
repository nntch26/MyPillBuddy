
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
    path("ShowMedication/", ShowMedicationView.as_view(), name="url_showmedication"),
    path("ShowMedication/add/", AddMedicationView.as_view(), name="url_addmedication"),

    path("patient_list/", PatientListView.as_view(), name="url_patientlist"),
    path("patient_list/add/", PatientAddView.as_view(), name="url_addpatient"),
    path("patient_list/del/<int:patient_id>", PatientDelView.as_view(), name="url_delpatient"),


]
