from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empleado, MuestraAlcohol
from .forms import EmpleadoCreationForm
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from django.http import HttpResponse, JsonResponse
from io import StringIO
import os, csv
import threading
import uuid
import json
from django.core.cache import cache
from .analisis_ahp import AnalizadorAHP

class EmpleadoAdmin(UserAdmin):
    # Formulario para crear usuarios
    add_form = EmpleadoCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'identificacion',
                'email',
                'first_name',
                'last_name',
                'departamento',
                'password1',
                'password2'
            ),
        }),
    )
    
    # Campos a mostrar en el listado
    list_display = (
        'username',
        'email',
        'identificacion',
        'departamento',
        'is_staff'
    )
    
    # Filtros
    list_filter = ('departamento', 'is_staff')
    
    # Plantilla personalizada
    change_list_template = 'admin/medidor/empleado/change_list.html'
    
    # Campos editables
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'identificacion',
                'departamento',
                'telefono',
                'fecha_ingreso'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    def changelist_view(self, request, extra_context=None):
        """Agregar contexto para el botón de importar y dashboard AHP."""
        extra_context = extra_context or {}
        extra_context['import_csv_url'] = 'import-csv/'
        extra_context['dashboard_ahp_url'] = 'dashboard-ahp/'
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='medidor_empleado_import_csv'),
            path('import-csv/status/<str:job_id>/', self.admin_site.admin_view(self.import_status_view), name='medidor_empleado_import_status'),
            path('dashboard-ahp/', self.admin_site.admin_view(self.dashboard_ahp_view), name='medidor_empleado_dashboard_ahp'),
            path('dashboard-ahp/export-csv/', self.admin_site.admin_view(self.export_ahp_csv), name='medidor_empleado_export_ahp_csv'),
            path('dashboard-ahp/export-pdf/', self.admin_site.admin_view(self.export_ahp_pdf), name='medidor_empleado_export_ahp_pdf'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        """Vista para subir CSVs desde el panel de administración y lanzarlos a la BD.
        Valida duplicados por `identificacion` antes de ejecutar la importación.
        """
        if request.method == 'POST':
            empleados_file = request.FILES.get('empleados_csv')
            muestras_file = request.FILES.get('muestras_csv')

            if not empleados_file and not muestras_file:
                messages.error(request, 'No se seleccionó ningún archivo.')
                return redirect('..')

            upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            empleados_path = ''
            muestras_path = ''

            # Guardar archivos recibidos
            if empleados_file:
                empleados_path = os.path.join(upload_dir, empleados_file.name)
                with open(empleados_path, 'wb') as f:
                    for chunk in empleados_file.chunks():
                        f.write(chunk)

            if muestras_file:
                muestras_path = os.path.join(upload_dir, muestras_file.name)
                with open(muestras_path, 'wb') as f:
                    for chunk in muestras_file.chunks():
                        f.write(chunk)

            # Validar duplicados en empleados (por identificacion)
            duplicates = []
            nuevos = 0
            if empleados_path:
                try:
                    with open(empleados_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            ident = row.get('identificacion') or row.get('empleado_identificacion')
                            if not ident:
                                continue
                            from .models import Empleado as EmplModel
                            if EmplModel.objects.filter(identificacion=ident).exists():
                                duplicates.append(ident)
                            else:
                                nuevos += 1
                except Exception as e:
                    messages.warning(request, f'Error al validar empleados: {e}')

            # Informar y ejecutar comando de carga — se lanzará en background si la petición es AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Crear job id y registrar en cache
                job_id = str(uuid.uuid4())
                cache_key = f'import_job_{job_id}'
                cache.set(cache_key, {'status': 'queued', 'progress': 0, 'output': ''}, timeout=60*60)

                def run_import(job_key, empleados_path, muestras_path):
                    try:
                        cache_data = cache.get(job_key) or {}
                        cache_data.update({'status': 'running', 'progress': 1})
                        cache.set(job_key, cache_data, timeout=60*60)

                        class CacheWriter:
                            def __init__(self, key):
                                self.key = key
                                self._lines = 0

                            def write(self, data):
                                if not data:
                                    return
                                d = str(data)
                                cache_data = cache.get(self.key) or {'status': 'running', 'progress': 0, 'output': ''}
                                cache_data['output'] = (cache_data.get('output','') + d)[-20000:]
                                # actualizar progreso heurísticamente basado en número de líneas
                                self._lines += d.count('\n')
                                cache_data['progress'] = min(95, cache_data.get('progress',0) + d.count('\n') )
                                cache.set(self.key, cache_data, timeout=60*60)

                            def flush(self):
                                pass

                        writer = CacheWriter(job_key)
                        cmd_args = []
                        if empleados_path:
                            cmd_args += ['--empleados', empleados_path]
                        if muestras_path:
                            cmd_args += ['--muestras', muestras_path]

                        call_command('cargar_datos_csv', *cmd_args, stdout=writer)

                        # marcar completado
                        cache_data = cache.get(job_key) or {}
                        cache_data['status'] = 'done'
                        cache_data['progress'] = 100
                        cache.set(job_key, cache_data, timeout=60*60)

                    except Exception as e:
                        cache_data = cache.get(job_key) or {}
                        cache_data['status'] = 'error'
                        cache_data['output'] = cache_data.get('output','') + f"\nError: {e}"
                        cache.set(job_key, cache_data, timeout=60*60)

                # iniciar thread
                t = threading.Thread(target=run_import, args=(cache_key, empleados_path, muestras_path), daemon=True)
                t.start()

                return JsonResponse({'job_id': job_id})

            # petición normal (no-AJAX): ejecutar sincronamente y mostrar resultado
            out = StringIO()
            try:
                cmd_args = []
                if empleados_path:
                    cmd_args += ['--empleados', empleados_path]
                if muestras_path:
                    cmd_args += ['--muestras', muestras_path]

                # Mostrar resumen previo
                if duplicates:
                    messages.info(request, f'{len(duplicates)} empleados ya existen y serán omitidos.')
                if nuevos:
                    messages.info(request, f'{nuevos} empleados nuevos serán importados.')

                call_command('cargar_datos_csv', *cmd_args, stdout=out)
                salida = out.getvalue()
                messages.success(request, 'Importación completada. Revisa el detalle abajo.')
                return render(request, 'admin/medidor/empleado/import_result.html', {'salida': salida, **self.admin_site.each_context(request)})

            except Exception as e:
                messages.error(request, f'Error al ejecutar la importación: {e}')
                return redirect('..')

        # GET -> mostrar formulario
        context = self.admin_site.each_context(request)
        return render(request, 'admin/medidor/empleado/import_csv.html', context)

    def import_status_view(self, request, job_id):
        """Devuelve el estado JSON del job de importación."""
        cache_key = f'import_job_{job_id}'
        data = cache.get(cache_key)
        if not data:
            return JsonResponse({'status': 'not_found'}, status=404)
        # Limitar salida devuelta para no enviar megas
        out = data.get('output','')
        return JsonResponse({'status': data.get('status','unknown'), 'progress': data.get('progress',0), 'output_tail': out[-500:]})

    def dashboard_ahp_view(self, request):
        """
        Dashboard AHP: Calcula el riesgo de alcohol usando el método AHP (Rating Model).
        
        Soporta filtros:
        - departamento: Filtrar por departamento específico
        - fecha_inicio: Filtrar mediciones desde esta fecha
        - fecha_fin: Filtrar mediciones hasta esta fecha
        
        Pasos:
        1. Matriz de Criterios: Crea matriz 2x2 (Severidad vs Frecuencia)
        2. Obtiene datos de empleados con muestras positivas
        3. Normaliza valores (max_alcohol y cantidad_positivos)
        4. Calcula AHP scores (0-100)
        5. Prepara top 10 empleados por riesgo para Chart.js
        """
        try:
            # Obtener parámetros de filtro del request
            departamento = request.GET.get('departamento', '').strip() or None
            fecha_inicio = request.GET.get('fecha_inicio', '').strip() or None
            fecha_fin = request.GET.get('fecha_fin', '').strip() or None
            orden = request.GET.get('orden', 'mayor')  # 'mayor' o 'menor'
            
            # Instanciar analizador con pairwise_value = 3 (Severidad 3x más importante)
            analizador = AnalizadorAHP(pairwise_value=3.0)
            
            # Ejecutar análisis completo (top 10 empleados) con filtros
            df_resultados = analizador.analizar(
                limite=10,
                departamento=departamento,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ordenar_descendente=(orden == 'mayor')
            )
            
            # Obtener opciones de filtro para los select
            departamentos = analizador.obtener_departamentos()
            rango_fechas = analizador.obtener_rango_fechas()
            
            if df_resultados.empty:
                context = self.admin_site.each_context(request)
                context.update({
                    'error_message': 'No hay datos disponibles para analizar con los filtros especificados.',
                    'title': 'Dashboard AHP - Análisis de Riesgo de Alcohol',
                    'departamentos': departamentos,
                    'rango_fechas': rango_fechas,
                    'filtros_aplicados': {
                        'departamento': departamento,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                    }
                })
                return render(request, 'admin/medidor/empleado/dashboard_ahp.html', context)
            
            # Preparar datos para Chart.js
            nombres = df_resultados['identificacion'].tolist()
            scores = df_resultados['ahp_score'].tolist()
            niveles_reales = df_resultados['max_alcohol'].tolist()
            niveles_riesgo = df_resultados['nivel_riesgo'].tolist()
            
            # Información de la matriz AHP
            info_ahp = {
                'peso_severidad': f"{analizador.peso_severidad:.4f}",
                'peso_frecuencia': f"{analizador.peso_frecuencia:.4f}",
                'pairwise_value': analizador.pairwise_value,
            }
            
            # Descripción de filtros aplicados
            filtros_descripcion = []
            if departamento:
                filtros_descripcion.append(f"Departamento: {departamento}")
            if fecha_inicio:
                filtros_descripcion.append(f"Desde: {fecha_inicio}")
            if fecha_fin:
                filtros_descripcion.append(f"Hasta: {fecha_fin}")
            
            context = self.admin_site.each_context(request)
            context.update({
                'title': 'Dashboard AHP - Análisis de Riesgo de Alcohol',
                'nombres_json': json.dumps(nombres, ensure_ascii=False),
                'scores_json': json.dumps([round(s, 2) for s in scores]),
                'niveles_reales_json': json.dumps([round(n, 2) for n in niveles_reales]),
                'niveles_riesgo_json': json.dumps(niveles_riesgo),
                'info_ahp': info_ahp,
                'resultados': df_resultados.to_dict('records'),
                'departamentos': departamentos,
                'rango_fechas': rango_fechas,
                'orden': orden,
                'filtros_aplicados': {
                    'departamento': departamento,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                },
                'filtros_descripcion': ', '.join(filtros_descripcion) if filtros_descripcion else 'Ninguno',
            })
            
            return render(request, 'admin/medidor/empleado/dashboard_ahp.html', context)
        
        except Exception as e:
            # Obtener opciones de filtro incluso si hay error
            try:
                analizador = AnalizadorAHP()
                departamentos = analizador.obtener_departamentos()
                rango_fechas = analizador.obtener_rango_fechas()
            except:
                departamentos = []
                rango_fechas = {'fecha_minima': None, 'fecha_maxima': None}
            
            context = self.admin_site.each_context(request)
            context.update({
                'error_message': f'Error al generar el dashboard: {str(e)}',
                'title': 'Dashboard AHP - Análisis de Riesgo de Alcohol',
                'departamentos': departamentos,
                'rango_fechas': rango_fechas,
            })
            return render(request, 'admin/medidor/empleado/dashboard_ahp.html', context)

    def export_ahp_csv(self, request):
        """Exporta resultados AHP a CSV"""
        try:
            # Obtener parámetros de filtro
            departamento = request.GET.get('departamento', '').strip()
            fecha_inicio = request.GET.get('fecha_inicio', '').strip()
            fecha_fin = request.GET.get('fecha_fin', '').strip()
            orden = request.GET.get('orden', 'mayor')  # 'mayor' o 'menor'
            
            # Convertir strings 'None' o vacíos a None
            departamento = departamento if departamento and departamento != 'None' else None
            fecha_inicio = fecha_inicio if fecha_inicio and fecha_inicio != 'None' else None
            fecha_fin = fecha_fin if fecha_fin and fecha_fin != 'None' else None
            
            # Ejecutar análisis
            analizador = AnalizadorAHP(pairwise_value=3.0)
            df_resultados = analizador.analizar(
                limite=None,
                departamento=departamento,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ordenar_descendente=(orden == 'mayor')
            )
            
            if df_resultados.empty:
                return HttpResponse('No hay datos para exportar', status=400)
            
            # Exportar a CSV
            csv_content = AnalizadorAHP.exportar_a_csv(df_resultados)
            
            # Preparar respuesta
            response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="ahp_analysis.csv"'
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al exportar: {str(e)}', status=500)

    def export_ahp_pdf(self, request):
        """Exporta resultados AHP a PDF"""
        try:
            # Obtener parámetros de filtro
            departamento = request.GET.get('departamento', '').strip()
            fecha_inicio = request.GET.get('fecha_inicio', '').strip()
            fecha_fin = request.GET.get('fecha_fin', '').strip()
            orden = request.GET.get('orden', 'mayor')  # 'mayor' o 'menor'
            
            # Convertir strings 'None' o vacíos a None
            departamento = departamento if departamento and departamento != 'None' else None
            fecha_inicio = fecha_inicio if fecha_inicio and fecha_inicio != 'None' else None
            fecha_fin = fecha_fin if fecha_fin and fecha_fin != 'None' else None
            
            # Ejecutar análisis
            analizador = AnalizadorAHP(pairwise_value=3.0)
            df_resultados = analizador.analizar(
                limite=None,
                departamento=departamento,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ordenar_descendente=(orden == 'mayor')
            )
            
            if df_resultados.empty:
                return HttpResponse('No hay datos para exportar', status=400)
            
            # Exportar a PDF
            pdf_content = AnalizadorAHP.exportar_a_pdf(df_resultados)
            
            # Preparar respuesta
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="ahp_analysis.pdf"'
            return response
            
        except ImportError as e:
            return HttpResponse(
                f'Error: reportlab no está instalado. Ejecuta: pip install reportlab',
                status=500
            )
        except Exception as e:
            return HttpResponse(f'Error al exportar: {str(e)}', status=500)

admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(MuestraAlcohol)
