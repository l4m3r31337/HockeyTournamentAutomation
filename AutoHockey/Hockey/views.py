# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from .forms import UserForm, UserProfileForm
# from .models import UserProfile
# from django.contrib.auth.models import User

import random
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SimpleRegistrationForm, UserProfileForm
from .models import UserProfile, Tournament, TournamentTable, TournamentResult
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction

def index(request):
    return render(request, 'hockey/index.html')

def registration(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = f"{form.cleaned_data['last_name']}_{form.cleaned_data['first_name']}".lower()
            user.save()

            UserProfile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data['middle_name'],
                last_name=form.cleaned_data['last_name']
            )
            login(request, user)
            return redirect('profile')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'hockey/registration.html', {'form': form})

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


@login_required
def tournament(request):
    # Получаем топ игроков из рейтинга
    players = UserProfile.objects.exclude(skill_level='').order_by('-skill_level')[:12]
    
    # Создаем турнирную таблицу
    if request.method == 'POST' and 'create_tournament' in request.POST:
        tournament = Tournament.objects.create(name=f"Турнир {Tournament.objects.count() + 1}")
        create_tournament_table(tournament, players)
        return redirect('tournament')
    
    # Сохраняем результаты турнира
    if request.method == 'POST' and 'save_results' in request.POST:
        tournament_id = request.POST.get('tournament_id')
        save_tournament_results(tournament_id)
        return redirect('rating')
    
    # Получаем активные турниры
    tournaments = Tournament.objects.filter(is_completed=False)

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
        'players_count': UserProfile.objects.exclude(skill_level='').count()
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
    
    # Создаем команды
    team_k = [goalkeepers[0]] + random.sample(field_players[:len(field_players)//2], 5)
    team_c = [goalkeepers[1]] + random.sample(field_players[len(field_players)//2:], 5)
    
    # Создаем таблицу турнира
    table = TournamentTable.objects.create(tournament=tournament, round_number=1)
    
    # Создаем записи результатов для каждого игрока
    for player in team_k:
        TournamentResult.objects.create(
            table=table,
            player=player.user,
            game_results={},
            team='K'
        )
    
    for player in team_c:
        TournamentResult.objects.create(
            table=table,
            player=player.user,
            game_results={},
            team='C'
        )

@transaction.atomic
def save_tournament_results(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    tables = tournament.tournamenttable_set.all()

    for table in tables:
        for result in table.tournamentresult_set.all():
            game_results = {}

            # Сохраняем 9 игр: game_2 to game_10
            for i in range(2, 11):
                field_name = f'game_{i}_{result.player.id}'
                score = request.POST.get(field_name, '0:0')
                game_results[f'game{i}'] = score

            result.game_results = game_results

            # Считаем разницу забитых/пропущенных
            goal_diff = 0
            for score in game_results.values():
                try:
                    scored, conceded = map(int, score.split(':'))
                    goal_diff += (scored - conceded)
                except (ValueError, AttributeError):
                    continue

            result.total_score = goal_diff
            result.save()

            # Обновляем рейтинг игрока
            profile = UserProfile.objects.get(user=result.player)
            try:
                current_rating = int(profile.skill_level)
            except ValueError:
                current_rating = 0

            profile.skill_level = str(current_rating + goal_diff * 10)
            profile.save()

    tournament.is_completed = True
    tournament.save()
