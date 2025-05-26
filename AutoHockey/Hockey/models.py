from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Мужской'), ('F', 'Женский')], blank=True)

    medical_doc = models.FileField(upload_to='medical_docs/', null=True, blank=True)
    medical_consent = models.BooleanField(default=False)

    identity_doc = models.FileField(upload_to='identity_docs/', null=True, blank=True)

    skill_level = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Профиль: {self.user.username}'
