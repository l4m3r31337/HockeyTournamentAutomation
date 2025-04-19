from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    surname = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        })
    )
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )
    patronymic = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Отчество'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер телефона'
        })
    )
    password1 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )

    password2 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('surname', 'name', 'patronymic', 'phone', 'password1', 'password2')


class ProfileForm(forms.Form):
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    middle_name = forms.CharField(label='Отчество', widget=forms.TextInput(attrs={'placeholder': 'Отчество'}))
    phone = forms.CharField(label='Номер телефона', widget=forms.TextInput(attrs={'placeholder': 'Номер телефона'}))
    age = forms.IntegerField(label='Возраст', widget=forms.NumberInput(attrs={'placeholder': 'Возраст'}))
    gender = forms.ChoiceField(label='Пол', choices=[('male', 'Мужской'), ('female', 'Женский')])

    skill_level = forms.ChoiceField(label='Уровень подготовки', choices=[
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ])

    position = forms.ChoiceField(label='Амплуа', choices=[
        ('forward', 'Нападающий'),
        ('goalkeeper', 'Вратарь'),
    ])

    medical_doc = forms.FileField(label='Медицинское заключение', required=False)
    medical_consent = forms.BooleanField(required=False)

    identity_doc = forms.FileField(label='Удостоверение личности', required=False)