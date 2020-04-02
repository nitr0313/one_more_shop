from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import UserEditForm, ProfileEditForm
from .models import Profile

from django.contrib.auth.decorators import login_required

# Create your views here.


def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'username':request.user})


def profile_edit(request):
    con = dict(
        section='dashboard',
        username=request.user
    )
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return redirect('dashboard')
    else:
        if request.user.is_authenticated:
            if request.user.is_active:
                user_form = UserEditForm(instance=request.user)
                profile_form = ProfileEditForm(instance=request.user.profile)
                con['user_form'] = user_form
                con['profile_form'] = profile_form
                return render(request,
                              'account/dashboard.html',
                              context=con
                              )
            else:
                return redirect('logout')
        else:
            return redirect('login')
