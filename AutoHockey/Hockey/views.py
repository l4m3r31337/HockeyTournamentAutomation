import random
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SimpleRegistrationForm, UserProfileForm
from .models import UserProfile, Tournament, TournamentTable, TournamentResult
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django import forms
import json
from itertools import combinations


def index(request):
    return render(request, 'hockey/index.html')

def registration(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Генерируем уникальный username
            base_username = f"{form.cleaned_data['last_name']}_{form.cleaned_data['first_name']}".lower()
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            user = User.objects.create_user(
                username=username,
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            UserProfile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data['middle_name'],
                last_name=form.cleaned_data['last_name'],
                email=email
            )
            
            login(request, user)
            return redirect('profile')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'hockey/registration.html', {'form': form})


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'placeholder': 'Email',
        'autofocus': True
    }))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'placeholder': 'Пароль'
    }))
    error_messages = {
        'invalid_login': "Пожалуйста, введите правильный email и пароль.",
        'inactive': "Этот аккаунт неактивен.",
    }

    def clean_username(self):
        email = self.cleaned_data.get('username')
        try:
            user = User.objects.get(email=email)
            return user.username
        except User.DoesNotExist:
            return email


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
            'rating': profile.skill_level,
            'age': profile.age,
            'position': profile.position
        })
    
    return render(request, 'hockey/rating.html', {'players': players_data})


def generate_round_robin_schedule(players):
    """Генерация расписания с ротацией игроков между командами"""
    num_players = len(players)
    num_games = 10  # Количество игр в турнире
    schedule = []
    
    for game_num in range(1, num_games + 1):
        # Разделяем игроков на две команды с ротацией
        if game_num % 2 == 0:
            blue_team = players[:num_players//2]
            red_team = players[num_players//2:]
        else:
            # Чередуем разделение для ротации
            blue_team = players[::2] + players[1::2][:num_players//2 - len(players[::2])]
            red_team = [p for p in players if p not in blue_team]
        
        # Сохраняем индексы игроков для каждой команды
        team_indices = {
            'blue': [i for i, p in enumerate(players) if p in blue_team],
            'red': [i for i, p in enumerate(players) if p in red_team]
        }
        schedule.append(team_indices)
    
    return schedule


@login_required
def tournament(request):
    players = UserProfile.objects.exclude(skill_level='').order_by('-skill_level')[:12]
    
    if request.method == 'POST' and 'create_tournament' in request.POST:
        tournament = Tournament.objects.create(name=f"Турнир {Tournament.objects.count() + 1}")
        
        # Создаем команды с балансировкой по вратарям
        goalkeepers = [p for p in players if p.position == 'Вратарь']
        field_players = [p for p in players if p.position != 'Вратарь']
        
        # Если вратарей меньше 2, назначаем случайных полевых игроков
        while len(goalkeepers) < 2:
            random_player = random.choice(field_players)
            random_player.position = 'Вратарь'
            random_player.save()
            goalkeepers.append(random_player)
            field_players.remove(random_player)
        
        # Создаем список всех игроков
        all_players = goalkeepers + field_players
        random.shuffle(all_players)
        
        # Генерируем расписание с ротацией
        schedule = generate_round_robin_schedule(all_players)
        
        # Создаем таблицу турнира
        table = TournamentTable.objects.create(
            tournament=tournament,
            round_number=1,
            schedule=json.dumps(schedule)
        )
        
        # Создаем записи результатов для каждого игрока
        for player in all_players:
            TournamentResult.objects.create(
                table=table,
                player=player.user,
                game_results={f"game{i}": "0:0" for i in range(1, 11)},
                total_score=0
            )
        
        return redirect('tournament')
    
    # Сохраняем результаты турнира
    if request.method == 'POST' and 'save_results' in request.POST:
        tournament_id = request.POST.get('tournament_id')
        table_id = request.POST.get('table_id')
        return save_tournament_results(request, tournament_id, table_id)
    
    # Получаем активные турниры
    tournaments = Tournament.objects.filter(is_completed=False).prefetch_related(
        'tournamenttable_set__tournamentresult_set__player__userprofile'
    )

    if request.method == 'POST' and 'rename_tournament' in request.POST:
        tournament_id = request.POST.get('edit_tournament_id')
        new_name = request.POST.get('new_name')
        Tournament.objects.filter(id=tournament_id).update(name=new_name)
        return redirect('tournament')
    
    if request.method == 'POST' and 'delete_tournament_id' in request.POST:
        tournament_id = request.POST.get('delete_tournament_id')
        Tournament.objects.filter(id=tournament_id).delete()
        return redirect('tournament')
    
    return render(request, 'hockey/tournament.html', {
        'tournaments': tournaments,
        'players_count': UserProfile.objects.exclude(skill_level='').count(),
        'range_1_10': range(1, 11),
    })

def create_tournament_table(tournament, players):
    # Разделяем игроков на две команды с одним вратарем в каждой
    goalkeepers = [p for p in players if p.position == 'Вратарь']
    field_players = [p for p in players if p.position != 'Вратарь']
    
    # Если вратарей меньше 2, назначаем случайных полевых игроков вратарями
    while len(goalkeepers) < 2:
        random_player = random.choice(field_players)
        random_player.position = 'Вратарь'
        random_player.save()
        goalkeepers.append(random_player)
        field_players.remove(random_player)
    
    # Создаем список всех игроков
    all_players = goalkeepers + field_players
    random.shuffle(all_players)
    
    # Генерируем расписание с ротацией
    schedule = generate_round_robin_schedule(all_players)
    
    # Создаем таблицу турнира
    table = TournamentTable.objects.create(
        tournament=tournament,
        round_number=1,
        team_blue_indices=json.dumps([i for i, p in enumerate(all_players) if p in blue_team]),
        schedule=schedule  # Сохраняем расписание
    )
    
    # Создаем записи результатов для каждого игрока
    for player in all_players:
        TournamentResult.objects.create(
            table=table,
            player=player.user,
            game_results={f"game{i}": "0:0" for i in range(1, 11)},
            total_score=0,
            team='C' if player in blue_team else 'K'
        )

@transaction.atomic
def save_tournament_results(request, tournament_id, table_id):
    tournament = Tournament.objects.get(id=tournament_id)
    table = TournamentTable.objects.get(id=table_id)
    
    # Получаем все результаты для таблицы
    results = table.tournamentresult_set.all()
    
    # Собираем результаты игр из формы
    game_results = {}
    for i in range(1, 11):
        red_score = request.POST.get(f'game_{i}_red', '0')
        blue_score = request.POST.get(f'game_{i}_blue', '0')
        game_results[f'game{i}'] = f"{red_score}:{blue_score}"
    
    # Обновляем результаты для каждого игрока
    for result in results:
        result.game_results = game_results
        
        # Вычисляем общий счет
        total_score = 0
        for game, score in game_results.items():
            red, blue = map(int, score.split(':'))
            if result.team == 'K':  # Красная команда
                total_score += (red - blue)
            else:  # Синяя команда
                total_score += (blue - red)
        
        result.total_score = total_score
        result.save()
    
    return redirect('tournament')
