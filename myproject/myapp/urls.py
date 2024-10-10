
from django.urls import path
from .views import *



urlpatterns = [
    path("", indexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="url_register"),
    path("login/", LoginView.as_view(), name="url_login"),
    path("logout/", LogoutView.as_view(), name="url_logout"),
]
