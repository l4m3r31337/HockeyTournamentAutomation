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
from collections import defaultdict

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


def generate_balanced_schedule(players):
    """
    players: список из 12 игроков. Первые два - вратари.
    Возвращает список из 10 игр: {'blue': [...], 'red': [...]}
    """
    num_players = len(players)
    num_games = 10
    assert num_players == 12, "Пока поддерживается только 12 игроков"

    # Инициализация счётчиков партнёрств и соперничеств
    teammate_counts = defaultdict(lambda: defaultdict(int))
    opponent_counts = defaultdict(lambda: defaultdict(int))

    schedule = []

    player_indices = list(range(num_players))
    gk1, gk2 = 0, 1  # индексы вратарей

    for game_num in range(num_games):
        # Вратари по умолчанию
        blue_team = [gk1]
        red_team = [gk2]

        # Кандидаты на остальные места
        fielders = [i for i in player_indices if i not in (gk1, gk2)]

        # Случайная перестановка для разнообразия
        random.shuffle(fielders)

        best_score = None
        best_split = None

        # Генерируем все возможные комбинации для разделения 10 игроков на 5 + 5
        from itertools import combinations

        for blue_f in combinations(fielders, 5):
            red_f = [i for i in fielders if i not in blue_f]

            curr_blue = blue_team + list(blue_f)
            curr_red = red_team + red_f

            # Оценка "разбалансированности"
            team_score = 0

            # Партнёры
            for team in [curr_blue, curr_red]:
                for i in team:
                    for j in team:
                        if i != j:
                            team_score += teammate_counts[i][j]

            # Противники
            for i in curr_blue:
                for j in curr_red:
                    team_score += opponent_counts[i][j]

            # Ищем вариант с минимальным количеством повторов
            if best_score is None or team_score < best_score:
                best_score = team_score
                best_split = {'blue': curr_blue, 'red': curr_red}

        # Обновляем счётчики
        blue = best_split['blue']
        red = best_split['red']

        for team in [blue, red]:
            for i in team:
                for j in team:
                    if i != j:
                        teammate_counts[i][j] += 1

        for i in blue:
            for j in red:
                opponent_counts[i][j] += 1
                opponent_counts[j][i] += 1

        schedule.append(best_split)

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
        
        # Определяем двух вратарей строго: gk1 и gk2
        random.shuffle(goalkeepers)
        gk1, gk2 = goalkeepers[0], goalkeepers[1]

        # Перемешиваем полевых
        random.shuffle(field_players)

        # Собираем итоговый список: сначала gk1, затем gk2, потом остальные
        all_players = [gk1, gk2] + field_players

        
        # Генерируем расписание с ротацией
        schedule = generate_balanced_schedule(all_players)
        
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
    schedule = generate_balanced_schedule(all_players)

    
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
    results = list(table.tournamentresult_set.select_related('player').all())

    # Собираем результаты игр из формы
    game_scores = {}
    for i in range(1, 11):
        red_score = int(request.POST.get(f'game_{i}_red', 0))
        blue_score = int(request.POST.get(f'game_{i}_blue', 0))
        game_scores[f'game{i}'] = (red_score, blue_score)

    # Обновляем данные каждого игрока
    for index, result in enumerate(results):
        total_score = 0
        game_result_data = {}

        for i in range(1, 11):
            game_key = f'game{i}'
            red_score, blue_score = game_scores[game_key]

            # Получаем команду игрока в этой игре (blue/red)
            team = table.get_team_for_player_in_game(index, i)

            # Сохраняем строку вида "2:0" или "0:3" для каждого игрока
            if team == 'blue':
                game_result_data[game_key] = f"{blue_score}:{red_score}"
                total_score += blue_score - red_score
            else:
                game_result_data[game_key] = f"{red_score}:{blue_score}"
                total_score += red_score - blue_score

        # Сохраняем результат
        result.game_results = game_result_data
        result.total_score = total_score
        result.save()

    return redirect('tournament')

