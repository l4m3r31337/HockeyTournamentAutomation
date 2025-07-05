from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SimpleRegistrationForm(UserCreationForm):
    middle_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Отчество'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email'
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'middle_name', 
            'phone', 'email', 'age', 'gender',
            'medical_doc', 'medical_consent',
            'identity_doc', 'skill_level', 'position'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder' : 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder' : 'Фамилия'}),
            'middle_name': forms.TextInput(attrs={'placeholder': 'Отчество'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Возраст'}),
            'gender': forms.Select(choices=[('M', 'Мужской'), ('F', 'Женский')]),
            'skill_level': forms.TextInput(attrs={'placeholder': 'Уровень подготовки'}),
            'position': forms.TextInput(attrs={'placeholder': 'Амплуа'}),
        }
