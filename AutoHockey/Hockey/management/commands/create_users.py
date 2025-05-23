from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Hockey.models import UserProfile
import random


# python manage.py create_users --clear

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates 200 test users with detailed profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing users and profiles before creation',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Deleting all users and profiles...')
            User.objects.all().delete()
        
        created_count = 0
        for i in range(1, 201):
            try:
                # Создаем пользователя
                user = User.objects.create_user(
                    username=f'Пользователь{i}',
                    password=f'user{i}pass123',
                    email=f'user{i}@example.com'
                )
                
                # Создаем профиль
                UserProfile.objects.create(
                    user=user,
                    age=random.randint(10, 20),
                    gender='M',
                    skill_level=str(random.randint(2000, 8000)),
                    medical_consent=random.choice([True, False]),
                    phone=f'+79{random.randint(10000000, 99999999)}'
                )
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {i}: {e}'))
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} users with profiles')
        )
