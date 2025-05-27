from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Empleado

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()
        if ' ' in username:
            raise forms.ValidationError("El nombre de usuario no puede contener espacios")
        return username

    def clean_password(self):
        return self.cleaned_data.get('password').strip()

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