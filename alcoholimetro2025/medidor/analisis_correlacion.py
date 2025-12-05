"""
Analizador de Correlación para diagnóstico de sensores y análisis demográfico.

Proporciona análisis de correlación entre:
- Variables técnicas (voltaje vs alcohol_ppm) - Diagnóstico de hardware
- Variables demográficas (antiguedad vs alcohol_ppm) - Análisis de causas humanas
"""

import numpy as np
import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Empleado, MuestraAlcohol


class AnalizadorCorrelacion:
    """Analizador de correlaciones para sensores y datos demográficos."""

    def __init__(self):
        """Inicializa el analizador de correlación."""
        self.df = None

    def obtener_datos(self):
        """
        Extrae datos de los modelos Empleado y MuestraAlcohol.
        
        Returns:
            pd.DataFrame: DataFrame con columnas:
                - voltaje (float)
                - alcohol_ppm (float)
                - fecha_ingreso (datetime)
                - departamento (str)
                - antiguedad_dias (int): Calculado como (ahora - fecha_ingreso).days
        """
        try:
            # Obtener todas las muestras de alcohol con su empleado relacionado
            muestras = MuestraAlcohol.objects.select_related('empleado').all()
            
            if not muestras.exists():
                # Retornar DataFrame vacío con las columnas esperadas
                return pd.DataFrame(columns=['voltaje', 'alcohol_ppm', 'fecha_ingreso', 'departamento', 'antiguedad_dias'])
            
            # Construir lista de diccionarios para crear el DataFrame
            datos = []
            ahora = timezone.now()
            
            for muestra in muestras:
                empleado = muestra.empleado
                
                # Validar que fecha_ingreso no sea nula
                if empleado.fecha_ingreso:
                    antiguedad_dias = (ahora.date() - empleado.fecha_ingreso).days
                else:
                    antiguedad_dias = None
                
                datos.append({
                    'voltaje': muestra.voltaje,
                    'alcohol_ppm': muestra.alcohol_ppm,
                    'fecha_ingreso': empleado.fecha_ingreso,
                    'departamento': empleado.departamento,
                    'antiguedad_dias': antiguedad_dias
                })
            
            # Crear DataFrame y guardar en la instancia
            self.df = pd.DataFrame(datos)
            
            # Limpiar valores nulos en columnas críticas para análisis
            self.df = self.df.dropna(subset=['voltaje', 'alcohol_ppm'])
            
            return self.df
        
        except Exception as e:
            print(f"Error al obtener datos: {str(e)}")
            return pd.DataFrame(columns=['voltaje', 'alcohol_ppm', 'fecha_ingreso', 'departamento', 'antiguedad_dias'])

    def analizar_sensores(self):
        """
        Analiza la correlación entre voltaje y alcohol_ppm para diagnóstico de hardware.
        
        Returns:
            dict: Diccionario con:
                - 'correlacion' (float): Coeficiente de Pearson
                - 'veredicto' (str): Diagnóstico del sensor
                - 'datos_scatter' (list): Lista de tuplas (voltaje, alcohol_ppm)
        """
        if self.df is None or self.df.empty:
            self.obtener_datos()
        
        if self.df.empty or len(self.df) < 2:
            return {
                'correlacion': None,
                'veredicto': 'Datos insuficientes para análisis',
                'datos_scatter': []
            }
        
        try:
            # Calcular correlación de Pearson
            correlacion = self.df['voltaje'].corr(self.df['alcohol_ppm'])
            
            # Manejar NaN en la correlación
            if pd.isna(correlacion):
                correlacion = None
                veredicto = 'No es posible calcular correlación (varianza insuficiente)'
            else:
                # Determinar veredicto basado en el valor de correlación
                if correlacion > 0.9:
                    veredicto = "Sensores calibrados (Linealidad excelente)"
                else:
                    veredicto = "Revisar sensores (Posible ruido o falta de calibración)"
            
            # Crear lista de tuplas para scatter plot
            datos_scatter = list(zip(
                self.df['voltaje'].tolist(),
                self.df['alcohol_ppm'].tolist()
            ))
            
            return {
                'correlacion': correlacion,
                'veredicto': veredicto,
                'datos_scatter': datos_scatter
            }
        
        except Exception as e:
            print(f"Error en analizar_sensores: {str(e)}")
            return {
                'correlacion': None,
                'veredicto': f'Error en análisis: {str(e)}',
                'datos_scatter': []
            }

    def analizar_demografia(self):
        """
        Analiza la correlación entre antigüedad y alcohol_ppm, y el riesgo por departamento.
        
        Returns:
            dict: Diccionario con:
                - 'correlacion_antiguedad' (float): Coeficiente de Pearson
                - 'conclusion_antiguedad' (str): Interpretación de la correlación
                - 'riesgo_por_departamento' (dict): Diccionario ordenado {departamento: promedio_ppm}
        """
        if self.df is None or self.df.empty:
            self.obtener_datos()
        
        if self.df.empty:
            return {
                'correlacion_antiguedad': None,
                'conclusion_antiguedad': 'Datos insuficientes para análisis',
                'riesgo_por_departamento': {}
            }
        
        try:
            resultados = {}
            
            # Analizar correlación entre antigüedad y alcohol_ppm
            df_con_antiguedad = self.df.dropna(subset=['antiguedad_dias'])
            
            if len(df_con_antiguedad) >= 2:
                correlacion_antiguedad = df_con_antiguedad['antiguedad_dias'].corr(
                    df_con_antiguedad['alcohol_ppm']
                )
            else:
                correlacion_antiguedad = None
            
            # Determinar conclusión sobre antigüedad
            if pd.isna(correlacion_antiguedad) or correlacion_antiguedad is None:
                conclusion_antiguedad = "No es posible calcular correlación (datos insuficientes)"
            elif correlacion_antiguedad < -0.3:
                conclusion_antiguedad = "Los empleados con mayor antigüedad tienen menos incidencias de alcohol"
            elif correlacion_antiguedad > 0.3:
                conclusion_antiguedad = "Los empleados más nuevos presentan más incidencias de alcohol"
            else:
                conclusion_antiguedad = "No hay correlación significativa entre antigüedad e incidencias de alcohol"
            
            resultados['correlacion_antiguedad'] = correlacion_antiguedad
            resultados['conclusion_antiguedad'] = conclusion_antiguedad
            
            # Calcular promedio de alcohol_ppm por departamento
            riesgo_por_departamento = self.df.groupby('departamento')['alcohol_ppm'].mean()
            
            # Ordenar de mayor a menor riesgo y convertir a diccionario
            riesgo_por_departamento = riesgo_por_departamento.sort_values(ascending=False)
            resultados['riesgo_por_departamento'] = riesgo_por_departamento.to_dict()
            
            return resultados
        
        except Exception as e:
            print(f"Error en analizar_demografia: {str(e)}")
            return {
                'correlacion_antiguedad': None,
                'conclusion_antiguedad': f'Error en análisis: {str(e)}',
                'riesgo_por_departamento': {}
            }
