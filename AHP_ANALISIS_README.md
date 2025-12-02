# Sistema AHP de Análisis de Riesgos de Alcohol

## Descripción

Se ha implementado un sistema completo de análisis usando el **Analytic Hierarchy Process (AHP)** para evaluar el riesgo de consumo de alcohol en empleados basándose en mediciones históricas.

## Características Principales

### 1. Modelos de Datos
- **CriterioAHP**: Define los criterios de evaluación y sus pesos
- **CalificacionEmpleado**: Almacena resultados del análisis para cada empleado

### 2. Criterios Predeterminados
- **Promedio de Alcohol** (peso: 35%) - Promedio de ppm en mediciones
- **Máximo de Alcohol** (peso: 35%) - Valor pico registrado
- **Frecuencia de Mediciones** (peso: 15%) - Cantidad de mediciones por día
- **Variabilidad** (peso: 15%) - Desviación estándar en niveles

### 3. Niveles de Riesgo
- **🟢 BAJO**: Puntuación < 50% y promedio < 50 ppm
- **🔵 MEDIO**: Puntuación 50-75% o promedio 50-80 ppm
- **🟡 ALTO**: Puntuación 75-100% o promedio > 80 ppm
- **🔴 CRÍTICO**: Máximo > 100 ppm

## Uso

### Inicializar el Sistema

Ejecuta el siguiente comando para crear los criterios predeterminados y realizar el análisis inicial:

```bash
python manage.py analizar_ahp --inicializar-criterios --mostrar-stats
```

### Ejecutar Análisis Posterior

Para actualizar las calificaciones de todos los empleados:

```bash
python manage.py analizar_ahp --mostrar-stats
```

### Ver Reportes en la Web

Accede a las siguientes URLs (requiere autenticación):

1. **Reporte de Riesgos**: `/reporte-riesgos/`
   - Vista general de todos los empleados
   - Estadísticas por nivel de riesgo
   - Ranking ordenado por puntuación

2. **Detalle de Empleado**: `/empleado/<identificacion>/`
   - Información personal
   - Puntuación AHP detallada
   - Últimas mediciones
   - Progreso temporal

3. **Criterios AHP**: `/criterios-ahp/`
   - Explicación del método AHP
   - Pesos de cada criterio
   - Fórmula de cálculo
   - Niveles de riesgo

## Arquitectura

### Servicio AnalizadorAHP (`medidor/analisis_ahp.py`)

**Métodos principales**:

```python
# Normalizar criterios
normalizar_criterios() -> dict

# Extraer métricas de un empleado
extraer_metricas_empleado(empleado) -> dict

# Calcular calificación individual
calcular_calificacion(empleado) -> dict

# Analizar todos los empleados
analizar_todos_empleados() -> list

# Obtener ranking
obtener_ranking_empleados(limite=10, ordenar_por='puntuacion') -> QuerySet

# Estadísticas generales
obtener_estadisticas_generales() -> dict
```

### Flujo de Cálculo

1. **Extracción de Métricas**
   - Promedio de ppm
   - Máximo de ppm
   - Desviación estándar
   - Frecuencia (muestras/día)

2. **Normalización Global**
   - Comparar con máximos de todos los empleados
   - Escalar a rango 0-1 (min-max)

3. **Ponderación AHP**
   - Aplicar pesos normalizados a cada métrica
   - Sumar valores ponderados
   - Escalar a rango 0-100%

4. **Clasificación**
   - Asignar nivel de riesgo basado en puntuación y máximos

## Modificar Criterios

Para cambiar los pesos de los criterios, accede al Django Admin y edita los objetos `CriterioAHP`:

```bash
python manage.py createsuperuser  # Si no existe
# Ir a http://localhost:8000/admin/
# Navega a "Criterios AHP"
# Edita los pesos y guarda
```

## Ejemplo de Salida

```
✅ Análisis completado
   • 101 empleados analizados

📊 Top 10 empleados por riesgo:

   1. EMP097     | CRITICO  | Puntuación:  75.46% | Promedio: 750.51 ppm
   2. EMP099     | CRITICO  | Puntuación:  56.71% | Promedio:  54.06 ppm
   ...

📈 Estadísticas generales:

   • Total de empleados: 101
   • Puntuación promedio: 54.08%
   • Puntuación máxima: 75.46%

   Distribución por riesgo:
   • Crítico: 101
   • Alto: 0
   • Medio: 0
   • Bajo: 0
```

## API REST

### Vistas Existentes

Las siguientes vistas se pueden acceder programáticamente:

- `reporte_riesgos_view()` - Retorna contexto con calificaciones
- `detalle_empleado_view()` - Detalles específicos por empleado
- `criterios_ahp_view()` - Información de criterios

## Próximas Mejoras

- [ ] API JSON para integración con sistemas externos
- [ ] Exportación a PDF/Excel de reportes
- [ ] Gráficos interactivos con Chart.js
- [ ] Histórico de análisis (versioning)
- [ ] Alertas automáticas por cambios de nivel de riesgo
- [ ] Configuración de umbrales personalizados por departamento
- [ ] Validación de criterios usando matriz de comparación pareada AHP

## Notas Técnicas

- La normalización es **global**: todos los empleados se comparan con los máximos registrados
- Los pesos se **normalizan automáticamente** para sumar 100%
- Los análisis se **actualizan en tiempo real** con cada ejecución del comando
- Los datos se persisten en la tabla `CalificacionEmpleado`
