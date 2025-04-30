from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SimpleRegistrationForm(UserCreationForm):
    middle_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Отчество'
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Пароль'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Подтверждение пароля'
    }))

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'middle_name', 'password1', 'password2']
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'middle_name', 'phone', 'age', 'gender',
            'medical_doc', 'medical_consent',
            'identity_doc', 'skill_level', 'position'
        ]
        widgets = {
            'middle_name': forms.TextInput(attrs={'placeholder': 'Отчество'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Возраст'}),
            'gender': forms.Select(choices=[('M', 'Мужской'), ('F', 'Женский')]),
            'skill_level': forms.TextInput(attrs={'placeholder': 'Уровень подготовки'}),
            'position': forms.TextInput(attrs={'placeholder': 'Амплуа'}),
        }
