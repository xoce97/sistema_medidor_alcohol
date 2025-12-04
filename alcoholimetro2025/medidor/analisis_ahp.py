"""
Analizador AHP (Rating Model) para cálculo de riesgo de alcohol en empleados.

Compara Severidad (máximo alcohol detectado) vs Frecuencia (cantidad de mediciones positivas)
usando una matriz AHP 2x2 para obtener pesos, luego normaliza y calcula scores.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from django.db.models import Max, Count, Q, Min
from django.utils import timezone
from .models import Empleado, MuestraAlcohol


class AnalizadorAHP:
    """Analizador AHP para rating de riesgo de alcohol."""

    def __init__(self, pairwise_value=3.0):
        """
        Inicializa el analizador AHP.
        
        Args:
            pairwise_value: Valor de comparación Severidad vs Frecuencia.
                           Si > 1, severidad es más importante.
                           Si < 1, frecuencia es más importante.
                           Por defecto 3.0 (Severidad 3x más importante).
        """
        self.pairwise_value = pairwise_value
        self._calcular_pesos()

    def _calcular_pesos(self):
        """Calcula los pesos usando la matriz AHP 2x2."""
        # Matriz de comparación pareada: [1, a; 1/a, 1]
        # donde a = pairwise_value (Severidad vs Frecuencia)
        matriz = np.array([
            [1.0, self.pairwise_value],
            [1.0 / self.pairwise_value, 1.0]
        ])
        
        # Calcular autovectores y autovalores
        autovalores, autovectores = np.linalg.eig(matriz)
        
        # El vector propio principal corresponde al autovalor máximo
        idx_max = np.argmax(autovalores.real)
        vector_propio = autovectores[:, idx_max].real
        
        # Normalizar el vector propio para que sume 1
        self.pesos = vector_propio / vector_propio.sum()
        self.peso_severidad = float(self.pesos[0])
        self.peso_frecuencia = float(self.pesos[1])

    def obtener_datos_empleados(self, departamento=None, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos de empleados con muestras positivas de la base de datos.
        
        Args:
            departamento: Filtrar por departamento (opcional)
            fecha_inicio: Fecha de inicio para filtrar muestras (datetime o string 'YYYY-MM-DD')
            fecha_fin: Fecha de fin para filtrar muestras (datetime o string 'YYYY-MM-DD')
        
        Returns:
            pd.DataFrame: DataFrame con columnas ['empleado_id', 'nombre', 'identificacion',
                          'departamento', 'max_alcohol', 'cantidad_positivos']
        """
        # Construir filtros
        filtro_muestras = Q(muestras__alcohol_ppm__gt=0)
        
        # Filtrar por rango de fechas si se proporciona
        if fecha_inicio:
            if isinstance(fecha_inicio, str):
                fecha_inicio = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            filtro_muestras &= Q(muestras__fecha__gte=fecha_inicio)
        
        if fecha_fin:
            if isinstance(fecha_fin, str):
                fecha_fin = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            # Sumar 1 día para incluir todo el día final
            fecha_fin_ajustada = fecha_fin.replace(hour=23, minute=59, second=59)
            filtro_muestras &= Q(muestras__fecha__lte=fecha_fin_ajustada)
        
        # Filtrar empleados
        empleados_queryset = Empleado.objects.filter(filtro_muestras).distinct()
        
        # Aplicar filtro de departamento si se proporciona
        if departamento:
            empleados_queryset = empleados_queryset.filter(departamento=departamento)

        datos = []
        for empleado in empleados_queryset:
            # Construir filtro de muestras para este empleado
            muestras_filter = Q(alcohol_ppm__gt=0)
            
            if fecha_inicio:
                muestras_filter &= Q(fecha__gte=fecha_inicio)
            
            if fecha_fin:
                muestras_filter &= Q(fecha__lte=fecha_fin_ajustada)
            
            # Obtener stats de muestras positivas
            stats = empleado.muestras.filter(muestras_filter).aggregate(
                max_alcohol=Max('alcohol_ppm'),
                cantidad_positivos=Count('id')
            )
            
            if stats['max_alcohol'] and stats['cantidad_positivos']:
                datos.append({
                    'empleado_id': empleado.id,
                    'nombre': empleado.nombre,
                    'identificacion': empleado.identificacion,
                    'departamento': empleado.departamento,
                    'max_alcohol': stats['max_alcohol'],
                    'cantidad_positivos': stats['cantidad_positivos'],
                })
        
        df = pd.DataFrame(datos)
        return df

    def normalizar_datos(self, df):
        """
        Normaliza los valores de max_alcohol y cantidad_positivos usando Max-Normalization.
        
        Fórmula: valor_normalizado = valor / max(valor)
        
        Args:
            df: DataFrame con datos de empleados.
            
        Returns:
            pd.DataFrame: DataFrame con columnas adicionales normalizadas.
        """
        if df.empty:
            return df
        
        # Max-Normalization
        df['severidad_norm'] = df['max_alcohol'] / df['max_alcohol'].max()
        df['frecuencia_norm'] = df['cantidad_positivos'] / df['cantidad_positivos'].max()
        
        return df

    def calcular_scores(self, df):
        """
        Calcula el AHP score para cada empleado.
        
        Fórmula: ahp_score = (severidad_norm * peso_severidad) + (frecuencia_norm * peso_frecuencia)
        
        Args:
            df: DataFrame con datos normalizados.
            
        Returns:
            pd.DataFrame: DataFrame con columna 'ahp_score' (0-100).
        """
        if df.empty:
            return df
        
        # Calcular score (0-100)
        df['ahp_score'] = (
            (df['severidad_norm'] * self.peso_severidad + 
             df['frecuencia_norm'] * self.peso_frecuencia) * 100
        )
        
        return df

    def asignar_nivel_riesgo(self, df):
        """
        Asigna nivel de riesgo basado en el score AHP.
        
        Args:
            df: DataFrame con columna 'ahp_score'.
            
        Returns:
            pd.DataFrame: DataFrame con columna 'nivel_riesgo'.
        """
        if df.empty:
            return df
        
        def clasificar_riesgo(score):
            if score >= 80:
                return 'CRÍTICO'
            elif score >= 60:
                return 'ALTO'
            elif score >= 40:
                return 'MEDIO'
            else:
                return 'BAJO'
        
        df['nivel_riesgo'] = df['ahp_score'].apply(clasificar_riesgo)
        return df

    def analizar(self, limite=None, departamento=None, fecha_inicio=None, fecha_fin=None, ordenar_descendente=True):
        """
        Ejecuta el análisis completo AHP.
        
        Args:
            limite: Número máximo de empleados a retornar (ordenados por riesgo).
                   Si None, retorna todos.
            departamento: Filtrar por departamento (opcional)
            fecha_inicio: Fecha de inicio para filtrar muestras (opcional)
            fecha_fin: Fecha de fin para filtrar muestras (opcional)
            ordenar_descendente: Si True, ordena de mayor a menor riesgo (default).
                                Si False, ordena de menor a mayor riesgo.
        
        Returns:
            pd.DataFrame: DataFrame con análisis completo, ordenado por ahp_score.
        """
        # 1. Obtener datos (con filtros)
        df = self.obtener_datos_empleados(
            departamento=departamento,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        if df.empty:
            return df
        
        # 2. Normalizar
        df = self.normalizar_datos(df)
        
        # 3. Calcular scores
        df = self.calcular_scores(df)
        
        # 4. Asignar niveles de riesgo
        df = self.asignar_nivel_riesgo(df)
        
        # Ordenar por score (descendente por defecto = mayor riesgo primero)
        df = df.sort_values('ahp_score', ascending=not ordenar_descendente)
        
        # Aplicar límite si se especifica
        if limite:
            df = df.head(limite)
        
        return df

    @staticmethod
    def obtener_departamentos():
        """
        Obtiene lista de departamentos únicos de empleados con muestras positivas.
        
        Returns:
            list: Lista de nombres de departamentos (ordenada)
        """
        departamentos = (
            Empleado.objects.filter(muestras__alcohol_ppm__gt=0)
            .values_list('departamento', flat=True)
            .distinct()
            .order_by('departamento')
        )
        return list(departamentos)

    @staticmethod
    def obtener_rango_fechas():
        """
        Obtiene el rango de fechas de muestras en la base de datos.
        
        Returns:
            dict: {'fecha_minima': datetime, 'fecha_maxima': datetime}
        """
        stats = MuestraAlcohol.objects.filter(
            alcohol_ppm__gt=0
        ).aggregate(
            fecha_min=Min('fecha'),
            fecha_max=Max('fecha')
        )
        return {
            'fecha_minima': stats['fecha_min'],
            'fecha_maxima': stats['fecha_max']
        }

    @staticmethod
    def exportar_a_csv(df, filename='ahp_analysis.csv'):
        """
        Exporta DataFrame a CSV.
        
        Args:
            df: DataFrame con resultados del análisis
            filename: Nombre del archivo CSV
            
        Returns:
            str: Contenido CSV como string
        """
        # Seleccionar y renombrar columnas para exportación
        df_export = df[[
            'identificacion', 'nombre', 'departamento',
            'max_alcohol', 'cantidad_positivos',
            'ahp_score', 'nivel_riesgo'
        ]].copy()
        
        df_export.columns = [
            'Identificación', 'Nombre', 'Departamento',
            'Max Alcohol (ppm)', 'Mediciones Positivas',
            'Score AHP (%)', 'Nivel de Riesgo'
        ]
        
        return df_export.to_csv(index=False, encoding='utf-8-sig')

    @staticmethod
    def exportar_a_pdf(df, titulo='Análisis AHP de Riesgo de Alcohol'):
        """
        Exporta DataFrame a PDF usando reportlab.
        
        Args:
            df: DataFrame con resultados del análisis
            titulo: Título del reporte
            
        Returns:
            bytes: Contenido PDF como bytes
        """
        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            from datetime import datetime
            
            # Crear buffer en memoria
            buffer = BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle(
                'Titulo',
                parent=estilos['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=12,
                alignment=1
            )
            
            estilo_fecha = ParagraphStyle(
                'Fecha',
                parent=estilos['Normal'],
                fontSize=10,
                textColor=colors.grey,
                spaceAfter=20,
                alignment=1
            )
            
            # Título
            titulo_para = Paragraph(f"📊 {titulo}", estilo_titulo)
            elementos.append(titulo_para)
            
            # Fecha
            fecha_para = Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilo_fecha)
            elementos.append(fecha_para)
            
            # Preparar datos para tabla
            datos_tabla = [['Identificación', 'Nombre', 'Dpto.', 'Max PPM', 'Med. Pos.', 'Score (%)', 'Riesgo']]
            
            for _, row in df.iterrows():
                datos_tabla.append([
                    str(row['identificacion']),
                    str(row['nombre']),
                    str(row['departamento'])[:10],
                    f"{row['max_alcohol']:.2f}",
                    str(row['cantidad_positivos']),
                    f"{row['ahp_score']:.2f}",
                    str(row['nivel_riesgo'])
                ])
            
            # Crear tabla
            tabla = Table(datos_tabla, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            
            # Estilo tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ])
            
            tabla.setStyle(estilo_tabla)
            elementos.append(tabla)
            
            # Construir PDF
            doc.build(elementos)
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            raise ImportError("reportlab no está instalado. Instala con: pip install reportlab")
