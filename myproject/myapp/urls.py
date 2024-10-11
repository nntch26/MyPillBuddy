
from django.urls import path
from .views import *



urlpatterns = [
    path("", indexView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("register/", RegisterView.as_view(), name="url_register"),
    path("login/", LoginView.as_view(), name="url_login"),
    path("logout/", LogoutView.as_view(), name="url_logout"),
    path("profile/", ProfileView.as_view(), name="url_profile"),
    path("history/", HistoryView.as_view(), name="url_history"),
    path("medication/", MedicationView.as_view(), name="url_medication"),

    # doctor
    path("doctor/", DoctorView.as_view(), name="url_doctor"),
    path("addmedication/", AddMedicationView.as_view(), name="url_addmedication"),

]
