from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Empleado

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

class EmpleadoCreationForm(UserCreationForm):
    class Meta:
        model = Empleado
        fields = (
            'username',
            'identificacion',
            'email',
            'first_name',
            'last_name',
            'departamento'
        )