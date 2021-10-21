from django.contrib import messages
from django.shortcuts import render

########################

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, ProfileInfoForm, ProfileInfoUpdateForm, ProfilePicsUpdateForm

from .models import User


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def profile(request):
    get_usertype = request.user.user_type
    if get_usertype == 1:
        usertype = 'Administrator'
    elif get_usertype == 2:
        usertype = 'Secretary'
    else:
        usertype = 'Basic User'

    info_form = ProfileInfoForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': info_form, 'usertype': usertype})


def profile_info(request):
    if request.method == 'POST':
        u_form = ProfileInfoUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile:profile_info')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update profile')
    else:
        u_form = ProfileInfoUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_details.html', {'form': u_form})


def profile_pics(request):
    if request.method == 'POST':
        p_form = ProfilePicsUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Profile Picture Updated Successfully')
            return redirect('profile:profile_picture')
        else:
            messages.error(request, 'Something Went Wrong, Unable to update profile picture')
    else:
        p_form = ProfilePicsUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile_pics.html', {'form': p_form})


def profile_password(request):
    return render(request, 'accounts/profile_pword.html')
