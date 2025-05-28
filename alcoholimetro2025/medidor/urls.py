from django.urls import path
 
from .views import (
    inicio_view,
    logout_view,
    dashboard_view,
    recibir_datos,
    control_medicion,
    CustomLoginView,
    estado_medicion_view
)

urlpatterns = [
    path('', inicio_view, name='inicio'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('control-medicion/', control_medicion, name='control_medicion'),
    path('api/recibir-datos/', recibir_datos, name='recibir_datos'),
    path("api/estado-medicion/", estado_medicion_view, name="estado_medicion"),
   
]
