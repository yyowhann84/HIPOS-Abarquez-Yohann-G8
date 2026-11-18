from django.contrib.auth import views as auth_views
from django.urls import path

from .views import HIPOSLoginView, profile, register

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", HIPOSLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", profile, name="profile"),
]
