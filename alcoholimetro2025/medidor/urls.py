from django.urls import path
 
from .views import (
    inicio_view,
    logout_view,
    index_view,
    recibir_datos,
    control_medicion,
    CustomLoginView,
    estado_medicion_view,
    reporte_riesgos_view,
    detalle_empleado_view,
    criterios_ahp_view,
    admin_dashboard_view,
    # nuevas vistas administrativas
    upload_csv_view,
    run_ahp_view,
)

urlpatterns = [
    path('', inicio_view, name='inicio'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('index/', index_view, name='index'),
    path('control-medicion/', control_medicion, name='control_medicion'),
    path('api/recibir-datos/', recibir_datos, name='recibir_datos'),
    path("api/estado-medicion/", estado_medicion_view, name="estado_medicion"),
    # Rutas de análisis AHP
    path('reporte-riesgos/', reporte_riesgos_view, name='reporte_riesgos'),
    path('empleado/<str:empleado_id>/', detalle_empleado_view, name='detalle_empleado'),
    path('criterios-ahp/', criterios_ahp_view, name='criterios_ahp'),
    # Dashboard administrativo
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    # Endpoints para administración (subir CSV y ejecutar análisis AHP)
    path('admin-dashboard/upload-csv/', upload_csv_view, name='admin_upload_csv'),
    path('admin-dashboard/run-ahp/', run_ahp_view, name='admin_run_ahp'),
]
