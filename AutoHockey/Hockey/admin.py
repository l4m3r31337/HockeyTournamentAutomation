from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = (
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