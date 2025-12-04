from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empleado, MuestraAlcohol
from .forms import EmpleadoCreationForm
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from io import StringIO
import os, csv
import threading
import uuid
from django.core.cache import cache
from django.http import JsonResponse

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
        """Agregar contexto para el botón de importar."""
        extra_context = extra_context or {}
        extra_context['import_csv_url'] = 'import-csv/'
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='medidor_empleado_import_csv'),
            path('import-csv/status/<str:job_id>/', self.admin_site.admin_view(self.import_status_view), name='medidor_empleado_import_status'),
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

admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(MuestraAlcohol)
