from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import JsonResponse
import json
from .models import Empleado, MuestraAlcohol
from .forms import LoginForm  # Asegúrate de importar tu formulario

# Vista de inicio (pública)
def inicio_view(request):
    return render(request, 'inicio.html')

# Vista de login

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login.html')

# Vista de logout
def logout_view(request):
    logout(request)
    return redirect('inicio')

# Dashboard (protegido)
#@login_required
def dashboard_view(request):
    muestras = MuestraAlcohol.objects.filter(empleado=request.user).order_by('-fecha')
    return render(request, 'dashboard.html', {'muestras': muestras})

# API para ESP32
@csrf_exempt
def recibir_datos_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            empleado = Empleado.objects.get(identificacion=data['empleado_id'])
            MuestraAlcohol.objects.create(
                empleado=empleado,
                valor_analogico=data['valor_analogico'],
                voltaje=data['voltaje'],
                alcohol_ppm=data['alcohol_ppm']
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)