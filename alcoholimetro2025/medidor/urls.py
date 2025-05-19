from django.urls import path
from .views import (
    inicio_view,
    login_view,
    logout_view,
    dashboard_view,
    recibir_datos_api
)

urlpatterns = [
    path('', inicio_view, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/muestras/', recibir_datos_api, name='api_muestras'),
]