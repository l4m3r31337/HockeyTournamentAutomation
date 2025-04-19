from django.urls import path
from django.urls import include
from .views import IndexView, profile_view, register

urlpatterns = [
    path('register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', profile_view, name='profile'),
    path('', IndexView.as_view(), name='home'),
]
