# Dashboard Administrativo AHP

## Descripción

El **Dashboard Administrativo** es una vista exclusiva para usuarios administradores que permite:

- ✅ Visualizar lista de todos los empleados con sus puntuaciones AHP
- ✅ Seleccionar un empleado para ver análisis detallado
- ✅ Gráfico de evolución de alcohol en últimos 30 días
- ✅ Métricas clave del empleado (promedio, máximo, frecuencia)
- ✅ Tabla de últimas mediciones
- ✅ Estadísticas generales de la organización

## Acceso

### URL
```
/admin-dashboard/
```

### Requisitos
- Usuario debe estar autenticado (`@login_required`)
- Usuario debe tener permisos de administrador (`is_staff=True` o `is_superuser=True`)
- Si accede un usuario no administrador: Error 403 (Forbidden)

## Características

### 1. Estadísticas Generales (Top)
Tarjetas resumen con:
- **Total Empleados**: Count de CalificacionEmpleado
- **Riesgo Promedio**: Promedio de puntuación_total
- **En Riesgo Crítico**: Conteo de empleados con nivel CRÍTICO
- **En Riesgo Bajo**: Conteo de empleados con nivel BAJO

### 2. Panel de Selección de Empleados (Izquierda)
- Lista scrollable de empleados ordenados por puntuación descendente (mayor riesgo primero)
- Cada item muestra:
  - ID del empleado (identificacion)
  - Nombre truncado
  - Porcentaje de puntuación (badge con color según riesgo)
  - Nivel de riesgo (CRÍTICO/ALTO/MEDIO/BAJO)
- Click para seleccionar empleado (actualiza con GET parameter: `?empleado_id=EMP001`)

### 3. Información del Empleado (Derecha - Arriba)
Tarjeta con datos básicos:
- Nombre completo
- ID (identificacion)
- Departamento
- Email

### 4. Puntuación AHP (Derecha - Tarjeta)
Displayable prominentemente:
- Puntuación total (0-100%)
- Nivel de riesgo con badge de color
- Barra de progreso con color según riesgo

**Colores por nivel:**
- BAJO (0-50%): Verde (success)
- MEDIO (50-75%): Amarillo (warning)
- ALTO (75-100%): Rojo (danger)
- CRÍTICO (max >= 100 ppm): Rojo oscuro (dark)

### 5. Métricas Detalladas
Cuatro tarjetas con:
- **Promedio PPM**: Alcohol promedio en ppm
- **Máximo PPM**: Máximo registrado (rojo)
- **Frecuencia**: Mediciones por día
- **Total Muestras**: Número de mediciones

### 6. Gráfico de Evolución (Chart.js)
Línea temporal de últimos 30 días con:
- **Eje X**: Fecha y hora de medición
- **Eje Y**: Niveles de alcohol en ppm
- **3 series de datos:**
  1. Azul: Línea de mediciones reales
  2. Naranja (punteada): Línea de promedio
  3. Rojo (punteada): Línea de máximo
- **Tooltip**: Muestra valor exacto al pasar mouse
- **Responsivo**: Se adapta al tamaño de pantalla

### 7. Tabla de Últimas Mediciones
Tabla con últimas 20 muestras del empleado:
- **Fecha**: Formato DD/MM/YYYY HH:MM
- **Valor Analógico**: Valor bruto del sensor
- **Voltaje**: Medición en voltios
- **Alcohol (ppm)**: Badge con color según nivel:
  - > 80 ppm: CRÍTICO (rojo)
  - > 50 ppm: ELEVADO (amarillo)
  - ≤ 50 ppm: NORMAL (verde)
- **Estado**: Etiqueta descriptiva (Crítico/Elevado/Normal)

## Estructura de Contexto

El view envía al template:

```python
context = {
    'empleados_list': QuerySet de CalificacionEmpleado (orden -puntuacion_total),
    'empleado_seleccionado': Objeto Empleado (si empleado_id GET param),
    'calificacion': CalificacionEmpleado del empleado (si seleccionado),
    'muestras_datos': Últimas 20 MuestraAlcohol del empleado (últimos 30 días),
    'chart_data': {
        'labels': [list de strings fecha/hora],
        'datos': [list de float PPM values],
        'max_ppm': float,
        'promedio_ppm': float
    },
    'stats': {
        'total_empleados': int,
        'promedio_puntuacion': float,
        'conteo_por_riesgo': {
            'BAJO': int,
            'MEDIO': int,
            'ALTO': int,
            'CRITICO': int
        }
    },
    'es_admin': True
}
```

## Uso Paso a Paso

### 1. Acceder al Dashboard
```
http://127.0.0.1:8000/admin-dashboard/
```

### 2. Ver Estadísticas Generales
Se cargan automáticamente las tarjetas con el resumen de la organización

### 3. Seleccionar Empleado
- Click en empleado de la lista izquierda
- URL se actualiza: `/admin-dashboard/?empleado_id=EMP001`
- Se carga información del empleado

### 4. Analizar Datos del Empleado
- Ver puntuación AHP y nivel de riesgo
- Observar gráfico de evolución (últimos 30 días)
- Analizar tabla de mediciones recientes
- Identificar patrones y anomalías

### 5. Tomar Decisiones
- Empleado en CRÍTICO: Acciones inmediatas
- Empleado en ALTO: Monitoreo cercano
- Empleado en MEDIO: Seguimiento regular
- Empleado en BAJO: Cumple normativa

## Notas Técnicas

### Seguridad
- Solo accesible a usuarios con `is_staff=True`
- Sin verificación: retorna 403 Forbidden
- Verificación implementada en view línea 127-128

### Performance
- Queries optimizadas con `select_related()` para empleado
- Filtro por últimos 30 días para gráfico (`timedelta(days=30)`)
- Tabla limitada a últimas 20 muestras

### Dependencias Frontend
- Bootstrap 5: Estilos y layouts
- Chart.js 3.9.1: Gráficos de línea
- Vanilla JavaScript: Inicialización de Chart

### Datos Dinámicos
- `|safe` filter en Django template para HTML crudo en Chart.js
- Format de etiquetas: `HH:MM` para claridad
- Valores PPM como flotantes para precisión

## Troubleshooting

### "Selecciona un empleado"
- Normal si está en `/admin-dashboard/` sin parámetro
- Click en un empleado de la lista para cargar datos

### Gráfico no aparece
- Verificar que empleado tenga muestras en últimos 30 días
- Revisar conexión a CDN Chart.js
- Abrirdevtools (F12) para ver errores JavaScript

### Error 403
- Verificar que usuario está logueado
- Verificar que usuario tiene `is_staff=True` en admin de Django
- Solo administradores pueden acceder

### Datos inconsistentes
- Ejecutar: `python manage.py analizar_ahp` para recalcular puntuaciones
- Verificar que CalificacionEmpleado está actualizado

## Futuras Mejoras

- [ ] Exportar reportes a PDF
- [ ] Filtros por rango de fechas
- [ ] Comparativa entre empleados
- [ ] Alertas automáticas por umbral
- [ ] Histórico de cambios en puntuación
- [ ] Gráfico de distribución de riesgos

---

**Creado:** {{ CURRENT_DATE }}
**Versión:** 1.0
**Requiere:** Django 5.2.8, Chart.js 3.9.1, Bootstrap 5
