from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Tournament, TournamentTable, TournamentResult
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = (
        'first_name',
        'last_name',
        'middle_name', 
        'phone', 
        'age', 
        'gender',
        'medical_doc',
        'medical_consent',
        'identity_doc',
        'skill_level',
        'position'
    )
    verbose_name_plural = 'Профили'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'skill_level', 'position')
    list_filter = ('gender', 'medical_consent')
    search_fields = ('user__username', 'middle_name', 'phone')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'middle_name', 'phone')
        }),
        ('Дополнительная информация', {
            'fields': ('age', 'gender', 'position', 'skill_level'),
        }),
        ('Документы', {
            'fields': ('medical_doc', 'medical_consent', 'identity_doc'),
        }),
    )


class TournamentResultInline(admin.TabularInline):
    model = TournamentResult
    extra = 0
    readonly_fields = ('player_link', 'total_score')
    fields = ('player_link', 'total_score')
    
    def player_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.player.id])
        return format_html('<a href="{}">{}</a>', url, obj.player.username)
    player_link.short_description = 'Игрок'
    
    def has_add_permission(self, request, obj=None):
        return False


class TournamentTableInline(admin.TabularInline):
    model = TournamentTable
    extra = 0
    readonly_fields = ('view_results_link', 'round_number', 'created_at')
    fields = ('round_number', 'created_at', 'view_results_link')
    
    def view_results_link(self, obj):
        url = reverse('admin:Hockey_tournamenttable_change', args=[obj.id])
        return format_html('<a href="{}">Просмотреть результаты</a>', url)
    view_results_link.short_description = 'Действия'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_completed', 'view_tables_link')
    list_filter = ('is_completed', 'date')
    search_fields = ('name',)
    inlines = [TournamentTableInline]
    
    def view_tables_link(self, obj):
        count = obj.tournamenttable_set.count()
        url = reverse('admin:Hockey_tournamenttable_changelist') + f'?tournament__id__exact={obj.id}'
        return format_html('<a href="{}">Таблицы ({})</a>', url, count)
    view_tables_link.short_description = 'Таблицы'


class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ('player', 'table', 'total_score', 'view_games')
    list_filter = ('table__tournament', 'table')
    search_fields = ('player__username',)
    
    def view_games(self, obj):
        games = []
        for i in range(1, 11):
            game_key = f'game{i}'
            score = obj.game_results.get(game_key, '0:0')
            games.append(f"{i}: {score}")
        return format_html("<br>".join(games))
    view_games.short_description = 'Результаты игр'


@admin.register(TournamentTable)
class TournamentTableAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'round_number', 'created_at', 'view_results_link')
    list_filter = ('tournament', 'round_number')
    search_fields = ('tournament__name',)
    inlines = [TournamentResultInline]
    
    def view_results_link(self, obj):
        count = obj.tournamentresult_set.count()
        url = reverse('admin:Hockey_tournamentresult_changelist') + f'?table__id__exact={obj.id}'
        return format_html('<a href="{}">Результаты ({})</a>', url, count)
    view_results_link.short_description = 'Результаты'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # Отображаем расписание в удобном формате
            schedule = obj.schedule
            if isinstance(schedule, str):
                try:
                    schedule = json.loads(schedule)
                except:
                    schedule = []
            
            schedule_html = "<h3>Расписание игр</h3><table><tr><th>Игра</th><th>Синяя команда</th><th>Красная команда</th></tr>"
            for i, game in enumerate(schedule, 1):
                blue_players = ", ".join([str(p+1) for p in game.get('blue', [])])
                red_players = ", ".join([str(p+1) for p in game.get('red', [])])
                schedule_html += f"<tr><td>{i}</td><td>{blue_players}</td><td>{red_players}</td></tr>"
            schedule_html += "</table>"
            
            form.base_fields['schedule'].help_text = mark_safe(schedule_html)
        return form


# Регистрируем TournamentResult с кастомным админ-классом
admin.site.register(TournamentResult, TournamentResultAdmin)