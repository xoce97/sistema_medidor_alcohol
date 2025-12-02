"""
Servicio de análisis usando el Método AHP (Analytic Hierarchy Process)
Realiza normalización de datos y cálculo de calificaciones de riesgo
"""

import numpy as np
from django.db.models import Avg, Max, Count, StdDev
from django.utils import timezone
from medidor.models import MuestraAlcohol, CriterioAHP, CalificacionEmpleado, Empleado


class AnalizadorAHP:
    """Clase para realizar análisis de datos usando AHP"""
    
    def __init__(self):
        """Inicializa el analizador con criterios activos"""
        self.criterios = CriterioAHP.objects.filter(activo=True)
        self.peso_total = sum(c.peso for c in self.criterios) or 1.0
    
    def normalizar_criterios(self):
        """Normaliza los pesos de los criterios para que sumen 1"""
        criterios_normalizados = {}
        for criterio in self.criterios:
            criterios_normalizados[criterio.nombre] = criterio.peso / self.peso_total
        return criterios_normalizados
    
    def extraer_metricas_empleado(self, empleado):
        """Extrae métricas de desempeño para un empleado"""
        muestras = MuestraAlcohol.objects.filter(empleado=empleado)
        
        if not muestras.exists():
            return None
        
        stats = muestras.aggregate(
            promedio_ppm=Avg('alcohol_ppm'),
            maximo_ppm=Max('alcohol_ppm'),
            desv_std=StdDev('alcohol_ppm'),
            count=Count('id')
        )
        
        # Calcular frecuencia (muestras por día)
        fecha_primera = muestras.first().fecha
        fecha_ultima = muestras.last().fecha
        dias_total = (fecha_ultima - fecha_primera).days + 1
        frecuencia = stats['count'] / max(dias_total, 1)
        
        return {
            'empleado': empleado,
            'promedio_ppm': stats['promedio_ppm'] or 0,
            'maximo_ppm': stats['maximo_ppm'] or 0,
            'desv_std': stats['desv_std'] or 0,
            'frecuencia': frecuencia,
            'numero_muestras': stats['count']
        }
    
    def normalizar_valor(self, valor, minimo, maximo):
        """Normaliza un valor entre 0 y 1 usando escalado min-max"""
        if maximo == minimo:
            return 0.5
        return (valor - minimo) / (maximo - minimo)
    
    def calcular_calificacion(self, empleado):
        """Calcula la calificación AHP final para un empleado"""
        metricas = self.extraer_metricas_empleado(empleado)
        
        if not metricas:
            return None
        
        # Obtener todos los valores para normalización global
        todos_empleados = Empleado.objects.filter(muestras__isnull=False).distinct()
        
        valores_globales = {
            'max_promedio_ppm': 0,
            'max_maximo_ppm': 0,
            'max_frecuencia': 0,
            'max_desv_std': 0,
        }
        
        for emp in todos_empleados:
            met = self.extraer_metricas_empleado(emp)
            if met:
                valores_globales['max_promedio_ppm'] = max(valores_globales['max_promedio_ppm'], met['promedio_ppm'])
                valores_globales['max_maximo_ppm'] = max(valores_globales['max_maximo_ppm'], met['maximo_ppm'])
                valores_globales['max_frecuencia'] = max(valores_globales['max_frecuencia'], met['frecuencia'])
                valores_globales['max_desv_std'] = max(valores_globales['max_desv_std'], met['desv_std'])
        
        # Normalizar métricas (escala 0-1)
        normalizadas = {
            'promedio_ppm_norm': self.normalizar_valor(
                metricas['promedio_ppm'], 0, valores_globales['max_promedio_ppm']
            ),
            'maximo_ppm_norm': self.normalizar_valor(
                metricas['maximo_ppm'], 0, valores_globales['max_maximo_ppm']
            ),
            'frecuencia_norm': self.normalizar_valor(
                metricas['frecuencia'], 0, valores_globales['max_frecuencia']
            ),
            'variabilidad_norm': self.normalizar_valor(
                metricas['desv_std'], 0, valores_globales['max_desv_std']
            ),
        }
        
        # Obtener pesos normalizados de criterios
        pesos = self.normalizar_criterios()
        
        # Calcular puntuación ponderada (escala 0-100)
        puntuacion = 0
        pesos_utilizados = 0
        
        # Mapear criterios a métricas
        mapeo_criterios = {
            'Promedio de Alcohol': 'promedio_ppm_norm',
            'Máximo de Alcohol': 'maximo_ppm_norm',
            'Frecuencia de Mediciones': 'frecuencia_norm',
            'Variabilidad': 'variabilidad_norm',
        }
        
        for nombre_criterio, metrica_key in mapeo_criterios.items():
            if nombre_criterio in pesos:
                peso = pesos[nombre_criterio]
                valor_normalizado = normalizadas.get(metrica_key, 0)
                puntuacion += peso * valor_normalizado * 100
                pesos_utilizados += peso
        
        # Normalizar si no se utilizaron todos los criterios
        if pesos_utilizados > 0:
            puntuacion = puntuacion / pesos_utilizados
        
        # Determinar nivel de riesgo
        nivel_riesgo = self.determinar_nivel_riesgo(puntuacion, metricas)
        
        return {
            'empleado': empleado,
            'puntuacion_total': round(puntuacion, 2),
            'nivel_riesgo': nivel_riesgo,
            'promedio_alcohol_ppm': round(metricas['promedio_ppm'], 2),
            'maximo_alcohol_ppm': round(metricas['maximo_ppm'], 2),
            'frecuencia_mediciones': round(metricas['frecuencia'], 2),
            'indice_variabilidad': round(metricas['desv_std'], 2),
            'numero_muestras': metricas['numero_muestras']
        }
    
    def determinar_nivel_riesgo(self, puntuacion, metricas):
        """Determina el nivel de riesgo basado en la puntuación y métricas"""
        # Criterios de decisión
        if metricas['maximo_ppm'] >= 100:
            return 'CRITICO'
        elif puntuacion >= 75 or metricas['promedio_ppm'] >= 80:
            return 'ALTO'
        elif puntuacion >= 50 or metricas['promedio_ppm'] >= 50:
            return 'MEDIO'
        else:
            return 'BAJO'
    
    def analizar_todos_empleados(self):
        """Analiza todos los empleados y actualiza sus calificaciones"""
        empleados = Empleado.objects.filter(muestras__isnull=False).distinct()
        resultados = []
        
        for empleado in empleados:
            calificacion = self.calcular_calificacion(empleado)
            if calificacion:
                # Crear o actualizar CalificacionEmpleado
                cal_obj, created = CalificacionEmpleado.objects.update_or_create(
                    empleado=empleado,
                    defaults={
                        'puntuacion_total': calificacion['puntuacion_total'],
                        'nivel_riesgo': calificacion['nivel_riesgo'],
                        'promedio_alcohol_ppm': calificacion['promedio_alcohol_ppm'],
                        'maximo_alcohol_ppm': calificacion['maximo_alcohol_ppm'],
                        'frecuencia_mediciones': calificacion['frecuencia_mediciones'],
                        'indice_variabilidad': calificacion['indice_variabilidad'],
                        'numero_muestras': calificacion['numero_muestras'],
                    }
                )
                resultados.append({
                    'empleado': empleado.identificacion,
                    'calificacion': calificacion,
                    'created': created
                })
        
        return resultados
    
    @staticmethod
    def obtener_ranking_empleados(limite=10, ordenar_por='puntuacion'):
        """Obtiene el ranking de empleados por riesgo"""
        if ordenar_por == 'puntuacion':
            calificaciones = CalificacionEmpleado.objects.all().order_by('-puntuacion_total')[:limite]
        elif ordenar_por == 'riesgo':
            # Ordenar por nivel de riesgo (CRÍTICO > ALTO > MEDIO > BAJO)
            orden_riesgo = {'CRITICO': 0, 'ALTO': 1, 'MEDIO': 2, 'BAJO': 3}
            calificaciones = sorted(
                CalificacionEmpleado.objects.all(),
                key=lambda x: (orden_riesgo.get(x.nivel_riesgo, 4), -x.puntuacion_total)
            )[:limite]
        else:
            calificaciones = CalificacionEmpleado.objects.all()[:limite]
        
        return calificaciones
    
    @staticmethod
    def obtener_estadisticas_generales():
        """Obtiene estadísticas generales del análisis"""
        calificaciones = CalificacionEmpleado.objects.all()
        
        if not calificaciones.exists():
            return None
        
        stats = calificaciones.aggregate(
            promedio_puntuacion=Avg('puntuacion_total'),
            max_puntuacion=Max('puntuacion_total'),
            min_puntuacion=Min('puntuacion_total') if hasattr(Min, '__call__') else 0,
        )
        
        # Contar por nivel de riesgo
        conteo_riesgo = {
            'CRITICO': calificaciones.filter(nivel_riesgo='CRITICO').count(),
            'ALTO': calificaciones.filter(nivel_riesgo='ALTO').count(),
            'MEDIO': calificaciones.filter(nivel_riesgo='MEDIO').count(),
            'BAJO': calificaciones.filter(nivel_riesgo='BAJO').count(),
        }
        
        return {
            'promedio_puntuacion': round(stats['promedio_puntuacion'], 2),
            'max_puntuacion': round(stats['max_puntuacion'], 2),
            'total_empleados': calificaciones.count(),
            'conteo_por_riesgo': conteo_riesgo
        }


from django.db.models import Min
