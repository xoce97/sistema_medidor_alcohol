from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from .models import Empleado, MuestraAlcohol, CalificacionEmpleado, CriterioAHP
from .forms import LoginForm  # Asegúrate de importar tu formulario
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
from .analisis_ahp import AnalizadorAHP
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
def index_view(request):
    muestras = MuestraAlcohol.objects.filter(empleado=request.user).order_by('-fecha')[:10]
    return render(request, 'index.html', {
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


# Vistas de análisis AHP
@login_required
def reporte_riesgos_view(request):
    """Vista que muestra el reporte de riesgos por empleado"""
    # Obtener ranking de empleados
    calificaciones = CalificacionEmpleado.objects.all().order_by('-puntuacion_total')
    
    # Obtener estadísticas generales
    stats = AnalizadorAHP.obtener_estadisticas_generales()
    
    # Contar por nivel de riesgo
    conteo_riesgo = {
        'critico': calificaciones.filter(nivel_riesgo='CRITICO').count(),
        'alto': calificaciones.filter(nivel_riesgo='ALTO').count(),
        'medio': calificaciones.filter(nivel_riesgo='MEDIO').count(),
        'bajo': calificaciones.filter(nivel_riesgo='BAJO').count(),
    }
    
    context = {
        'calificaciones': calificaciones[:50],  # Top 50
        'stats': stats,
        'conteo_riesgo': conteo_riesgo,
        'total_empleados': calificaciones.count(),
    }
    
    return render(request, 'reporte_riesgos.html', context)


@login_required
def detalle_empleado_view(request, empleado_id):
    """Vista que muestra el detalle de análisis de un empleado"""
    try:
        empleado = Empleado.objects.get(identificacion=empleado_id)
        calificacion = CalificacionEmpleado.objects.get(empleado=empleado)
        muestras = MuestraAlcohol.objects.filter(empleado=empleado).order_by('-fecha')[:20]
        
        context = {
            'empleado': empleado,
            'calificacion': calificacion,
            'muestras': muestras,
            'color_badge': calificacion.color_riesgo,
        }
        
        return render(request, 'detalle_empleado.html', context)
    except (Empleado.DoesNotExist, CalificacionEmpleado.DoesNotExist):
        return render(request, '404.html', status=404)


@login_required
def criterios_ahp_view(request):
    """Vista que muestra los criterios AHP utilizados"""
    criterios = CriterioAHP.objects.filter(activo=True).order_by('-peso')
    peso_total = sum(c.peso for c in criterios) or 1.0
    
    # Calcular pesos normalizados
    criterios_con_peso_norm = [
        {
            'criterio': c,
            'peso_normalizado': round((c.peso / peso_total) * 100, 2)
        }
        for c in criterios
    ]
    
    context = {
        'criterios': criterios_con_peso_norm,
        'peso_total': peso_total,
    }
    
    return render(request, 'criterios_ahp.html', context)


@login_required
def admin_dashboard_view(request):
    """Dashboard administrativo con análisis AHP - Solo administradores"""
    # Verificar permisos de administrador
    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, '403.html', status=403)
    
    # Obtener empleado seleccionado (por parámetro GET)
    empleado_id = request.GET.get('empleado_id')
    
    # Obtener lista de empleados con calificaciones
    empleados_list = CalificacionEmpleado.objects.select_related('empleado').order_by('-puntuacion_total')
    
    empleado_seleccionado = None
    calificacion = None
    muestras_datos = None
    chart_data = None
    
    if empleado_id:
        try:
            empleado_seleccionado = Empleado.objects.get(identificacion=empleado_id)
            calificacion = CalificacionEmpleado.objects.get(empleado=empleado_seleccionado)
            
            # Obtener muestras últimas 30 días
            from django.utils import timezone
            from datetime import timedelta
            
            hace_30_dias = timezone.now() - timedelta(days=30)
            muestras = MuestraAlcohol.objects.filter(
                empleado=empleado_seleccionado,
                fecha__gte=hace_30_dias
            ).order_by('fecha')
            
            # Preparar datos para gráfico
            if muestras.exists():
                chart_data = {
                    'labels': [m.fecha.strftime('%d/%m %H:%M') for m in muestras],
                    'datos': [float(m.alcohol_ppm) for m in muestras],
                    'max_ppm': float(calificacion.maximo_alcohol_ppm),
                    'promedio_ppm': float(calificacion.promedio_alcohol_ppm),
                }
            
            muestras_datos = muestras[:20]
            
        except (Empleado.DoesNotExist, CalificacionEmpleado.DoesNotExist):
            pass
    
    # Estadísticas generales
    stats = AnalizadorAHP.obtener_estadisticas_generales()
    
    context = {
        'empleados_list': empleados_list,
        'empleado_seleccionado': empleado_seleccionado,
        'calificacion': calificacion,
        'muestras_datos': muestras_datos,
        'chart_data': chart_data,
        'stats': stats,
        'es_admin': True,
    }
    
    return render(request, 'admin_dashboard.html', context)
