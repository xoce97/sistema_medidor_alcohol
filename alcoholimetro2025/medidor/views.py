from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from .models import Empleado, MuestraAlcohol
from .forms import LoginForm  # Asegúrate de importar tu formulario
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
import requests
import json

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(form.errors, status=400)
        return response

# Vista de inicio (pública)
def inicio_view(request):
    return render(request, 'inicio.html')

# Vista de logout
def logout_view(request):
    logout(request)
    return redirect('inicio')


@login_required
def dashboard_view(request):
    muestras = MuestraAlcohol.objects.filter(empleado=request.user).order_by('-fecha')[:10]
    return render(request, 'dashboard.html', {
        'muestras': muestras,
        'medicion_activa': cache.get(f'medicion_activa_{request.user.id}', False)
    })

@csrf_exempt
@require_POST
def control_medicion(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    action = request.POST.get('action')
    user = request.user
    
    # Actualizar estado en cache
    cache.set(f'medicion_activa_{user.id}', action == 'iniciar', timeout=None)
    
    # Notificar a la ESP32 solo al iniciar
    if action == 'iniciar':
        try:
            response = requests.post(
                "http://192.168.1.109/control-medicion",
                json={
                    'action': 'iniciar',
                    'empleado_id': user.id,
                    'nombre': user.get_full_name(),
                    'identificacion': user.identificacion
                },
                timeout=2
            )
            return JsonResponse({
                'status': 'Medición iniciada',
                'esp32_response': response.json()
            })
        except Exception as e:
            return JsonResponse({
                'status': 'Medición iniciada (ESP32 no notificada)',
                'warning': str(e)
            }, status=200)
    
    return JsonResponse({'status': 'Medición detenida'})

@csrf_exempt
@require_POST
def recibir_datos(request):
    try:
        data = json.loads(request.body)
        empleado = Empleado.objects.get(id=data['empleado_id'])
        
        MuestraAlcohol.objects.create(
            empleado=empleado,
            valor_analogico=data['valor_analogico'],
            voltaje=data['voltaje'],
            alcohol_ppm=data['alcohol_ppm']
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
