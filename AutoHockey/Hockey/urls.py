from django.urls import path
from Hockey.views import register
from django.views.generic import RedirectView
from django.urls import include

urlpatterns = [
    path('register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='register/', permanent=True)),
]
