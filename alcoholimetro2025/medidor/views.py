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
def recibir_datos(request):
    try:
        data = json.loads(request.body)
        
        # Validación básica
        required_fields = ['empleado_id', 'valor_analogico', 'voltaje', 'alcohol_ppm']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'status': 'error', 'message': f'Falta el campo {field}'}, status=400)

        empleado = Empleado.objects.get(id=data['empleado_id'])
        
        MuestraAlcohol.objects.create(
            empleado=empleado,
            valor_analogico=data['valor_analogico'],
            voltaje=data['voltaje'],
            alcohol_ppm=data['alcohol_ppm']
        )
        
        return JsonResponse({'status': 'success'})
    except Empleado.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def estado_medicion_view(request):
    empleado_id = request.GET.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'activa': False})

    estado = cache.get(f'medicion_activa_{empleado_id}', False)
    return JsonResponse({'activa': estado})

@csrf_exempt
@require_POST
def control_medicion(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    action = request.POST.get('action')
    user = request.user

    # Actualizar estado en cache
    cache.set(f'medicion_activa_{user.id}', action == 'iniciar', timeout=None)

    if action == 'iniciar':
        try:
            response = requests.post(
                "http://192.168.1.109/control-medicion",  # asegúrate que sea la IP actual de tu ESP32
                json={
                    'action': 'iniciar',
                    'empleado_id': user.id,
                    'nombre': user.get_full_name(),
                    'identificacion': user.identificacion
                },
                timeout=2
            )

            # Intentar parsear JSON
            try:
                esp32_response = response.json()
            except ValueError:
                esp32_response = {
                    'warning': 'Respuesta no válida de ESP32',
                    'raw': response.text  # Esto te ayudará a depurar
                }

            return JsonResponse({
                'status': 'Medición iniciada',
                'esp32_response': esp32_response
            })

        except Exception as e:
            return JsonResponse({
                'status': 'Medición iniciada (ESP32 no notificada)',
                'warning': str(e)
            }, status=200)

    return JsonResponse({'status': 'Medición detenida'})
