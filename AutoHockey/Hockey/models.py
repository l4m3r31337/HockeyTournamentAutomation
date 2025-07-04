from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Мужской'), ('F', 'Женский')], blank=True)

    medical_doc = models.FileField(upload_to='medical_docs/', null=True, blank=True)
    medical_consent = models.BooleanField(default=False)

    identity_doc = models.FileField(upload_to='identity_docs/', null=True, blank=True)

    skill_level = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Профиль: {self.user.username}'
    



class Tournament(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.date})"

class TournamentTable(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['round_number']

class TournamentResult(models.Model):
    table = models.ForeignKey(TournamentTable, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_results = models.JSONField()  # {'game2': '2:2', 'game3': '4:2', ...}
    total_score = models.IntegerField(default=0)
    team = models.CharField(max_length=1, choices=[('K', 'Команда K'), ('C', 'Команда C')])

    class Meta:
        ordering = ['-total_score']
