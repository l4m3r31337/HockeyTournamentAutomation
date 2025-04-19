from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, ProfileForm
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'Hockey/index.html'


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Название вашей стартовой страницы
    else:
        form = RegisterForm()
    return render(request, 'Hockey/registration.html', {'form': form})

def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Тут можно сохранить в БД или куда требуется
            print("Форма сохранена:", form.cleaned_data)
            return redirect('profile')  # Имя маршрута
    else:
        form = ProfileForm()

    return render(request, 'Hockey/profile.html', {'form': form})
