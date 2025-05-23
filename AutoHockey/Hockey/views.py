# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from .forms import UserForm, UserProfileForm
# from .models import UserProfile
# from django.contrib.auth.models import User

import random
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SimpleRegistrationForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'hockey/index.html')

def registration(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = f"{form.cleaned_data['last_name']}_{form.cleaned_data['first_name']}".lower()
            user.save()

            UserProfile.objects.create(
                user=user,
                middle_name=form.cleaned_data['middle_name']
            )
            login(request, user)
            return redirect('profile')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'hockey/registration.html', {'form': form})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'hockey/profile.html', {'form': form})


def rating(request):
    profiles = UserProfile.objects.exclude(skill_level='').order_by('-skill_level')
    
    players_data = []
    for profile in profiles:
        players_data.append({
            'name': profile.user.username,
            'rating': profile.skill_level
        })
    
    return render(request, 'hockey/rating.html', {'players': players_data})
