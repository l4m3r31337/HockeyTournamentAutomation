from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('registration/', views.registration, name='registration'),

    path('login/', auth_views.LoginView.as_view(template_name='hockey/login.html', form_class=views.EmailAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('rating/', views.rating, name='rating'),
    path('tournament/', views.tournament, name='tournament'),
]
