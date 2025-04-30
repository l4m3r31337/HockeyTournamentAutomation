from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('registration/', views.registration, name='registration'),
    path('rating/', views.rating, name='rating'),
    
]
