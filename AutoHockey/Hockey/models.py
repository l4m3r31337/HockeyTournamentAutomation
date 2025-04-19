from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    surname = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username