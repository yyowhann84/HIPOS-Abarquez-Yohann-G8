from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegistrationForm
from .models import UserProfile


class HIPOSLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        UserProfile.objects.create(user=user, role=UserProfile.Role.CLEANUP_MEMBER)
        login(request, user)
        messages.success(request, "Your HIPOS account has been created.")
        return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile was updated.")
        return redirect("profile")
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"form": form, "user_profile": user_profile})
