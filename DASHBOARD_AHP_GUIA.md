# Dashboard AHP - Guía de Uso

## 📊 Descripción General

El dashboard AHP implementa el método **AHP (Rating Model)** para analizar y calcular el riesgo de alcohol en empleados basándose en dos criterios principales:

1. **Severidad**: Máximo nivel de alcohol (ppm) detectado
2. **Frecuencia**: Cantidad de mediciones con valores positivos (> 0 ppm)

## 🔧 Tecnología Implementada

### Matriz de Criterios (AHP 2x2)
- Comparación pareada: Severidad vs Frecuencia
- Valor de comparación: **3.0** (Severidad es 3 veces más importante que Frecuencia)
- Matriz:
  ```
  [1.0,  3.0]
  [0.33, 1.0]
  ```

### Cálculo de Pesos
- Se calculan autovectores y autovalores usando NumPy
- Los pesos se normalizan para sumar 1.0
- Típicamente:
  - **Peso Severidad**: ~0.75
  - **Peso Frecuencia**: ~0.25

### Normalización (Max-Normalization)
```
valor_normalizado = valor / máximo(valor)
```

### Score AHP
```
ahp_score (0-100) = (severidad_norm * peso_severidad + frecuencia_norm * peso_frecuencia) * 100
```

### Clasificación de Riesgo
| Score | Nivel | Color |
|-------|-------|-------|
| ≥ 80% | CRÍTICO | Rojo |
| 60-79% | ALTO | Naranja |
| 40-59% | MEDIO | Amarillo |
| < 40% | BAJO | Verde |

## 🚀 Acceso al Dashboard

### Opción 1: Desde el Panel de Administración
1. Ve a `/admin/`
2. En la sección **Medidor** → **Empleados**
3. Haz clic en el botón **📊 Dashboard AHP** (parte superior)

### Opción 2: URL Directa
```
http://localhost:8000/admin/medidor/empleado/dashboard-ahp/
```

## 📈 Componentes del Dashboard

### Encabezado Informativo
Muestra:
- Peso de Severidad
- Peso de Frecuencia
- Comparación pareada (3:1)

### Gráfico Combinado (Chart.js)
- **Barras**: Score AHP (%) - Codificadas por color según nivel de riesgo
- **Línea**: Max Alcohol (ppm) - Muestra el nivel real detectado
- Eje Y izquierdo: Scores (0-100)
- Eje Y derecho: Ppm (escala variable)

### Tabla Detallada
Muestra los **Top 10 empleados** ordenados por riesgo:
- Identificación
- Nombre
- Max Alcohol (ppm)
- Mediciones Positivas
- Score AHP (%)
- Nivel de Riesgo (con badge de color)

## 🔍 Ejemplo de Interpretación

**Empleado 1:**
- Max Alcohol: 250 ppm (Severidad ALTA)
- Mediciones Positivas: 5 (Frecuencia MEDIA)
- Score AHP: 85% → **CRÍTICO**
- Interpretación: Alto riesgo debido principalmente a la severidad

**Empleado 2:**
- Max Alcohol: 50 ppm (Severidad BAJA)
- Mediciones Positivas: 20 (Frecuencia ALTA)
- Score AHP: 65% → **ALTO**
- Interpretación: Riesgo moderado por frecuencia frecuente de mediciones

## 🔍 Filtros Disponibles

El dashboard ahora incluye cuatro filtros poderosos para analizar datos específicos:

### 1. **Filtro por Departamento**
- Selecciona un departamento específico de la lista desplegable
- Muestra solo empleados de ese departamento
- La lista se auto-rellena con los departamentos que tienen datos

### 2. **Filtro de Fecha de Inicio**
- Selecciona la fecha desde la cual incluir mediciones
- Solo se consideran muestras posteriores o iguales a esta fecha
- Restricciones automáticas según el rango de datos disponibles

### 3. **Filtro de Fecha de Fin**
- Selecciona la fecha hasta la cual incluir mediciones
- Solo se consideran muestras anteriores o iguales a esta fecha (incluye todo el día)
- Restricciones automáticas según el rango de datos disponibles

### 4. **Filtro de Riesgo (Mayor/Menor)**
- **Mayor a Menor**: Muestra empleados de mayor a menor riesgo (empleados más peligrosos primero) - **DEFAULT**
- **Menor a Mayor**: Muestra empleados de menor a mayor riesgo - **EMPLEADOS SEGUROS PRIMERO** ✅
- Útil para identificar empleados con valores bajos/seguros

### Uso de Filtros
1. **Llenar filtros**: Completa los campos que desees utilizar
2. **Aplicar**: Haz clic en "🔎 Aplicar Filtros"
3. **Limpiar**: Haz clic en "🔄 Limpiar" para restablecer todos los filtros
4. **Estado**: El panel muestra qué filtros están activos

### Ejemplos de Uso

**Caso 1: Los 10 empleados MÁS en RIESGO**
- Departamento: (vacío)
- Ordenar: Mayor a Menor
- Verá los 10 empleados con mayor Score AHP

**Caso 2: Los 10 empleados MÁS SEGUROS (bajo riesgo)**
- Departamento: (vacío)
- Ordenar: Menor a Mayor ✅
- Verá los 10 empleados con menor Score AHP (valores bajos/seguros)

**Caso 3: Departamento específico - Orden por seguridad**
- Departamento: "Producción"
- Ordenar: Menor a Mayor
- Resultados del departamento de Producción ordenados de menor a mayor riesgo

**Caso 4: Rango temporal - Empleados de riesgo**
- Fecha Inicio: 2025-01-01
- Fecha Fin: 2025-02-28
- Ordenar: Mayor a Menor
- Empleados más peligrosos en ese período

## 📥 Exportación de Datos

El dashboard incluye dos opciones de exportación:

### **Exportar a CSV** 📥
- Botón verde "📥 CSV"
- Descarga un archivo Excel/CSV con todos los resultados
- Incluye: Identificación, Nombre, Departamento, Max PPM, Mediciones, Score, Riesgo
- Mantiene los filtros aplicados
- Perfecta para análisis en Excel o importar en otras herramientas

### **Exportar a PDF** 📄
- Botón verde "📄 PDF"
- Genera un reporte profesional en PDF
- Incluye: Encabezado, fecha de generación, tabla formateada, estilos
- Mantiene los filtros aplicados
- Ideal para reportes ejecutivos

#### Requisito para PDF
```bash
pip install reportlab
```



El dashboard necesita:
- ✅ Empleados en la base de datos (tabla `medidor_empleado`)
- ✅ Muestras de alcohol (tabla `medidor_muestraaalcohol`) con `alcohol_ppm > 0`

Si no hay datos, se mostrará un mensaje: *"No hay datos disponibles para analizar"*

## 🛠️ Dependencias Instaladas

```bash
numpy >= 1.24
pandas >= 1.5
django >= 4.0
chart.js (CDN)
```

## 📝 Notas Técnicas

### Archivos Creados/Modificados
1. `medidor/analisis_ahp.py` - Lógica principal del análisis AHP
2. `medidor/admin.py` - Vista `dashboard_ahp_view` y rutas
3. `medidor/templates/admin/medidor/empleado/dashboard_ahp.html` - Plantilla con Chart.js
4. `medidor/templates/admin/medidor/empleado/change_list.html` - Botón de acceso

### Métodos Principales (AnalizadorAHP)
- `__init(pairwise_value=3.0)` - Inicializa con matriz AHP
- `obtener_datos_empleados(departamento, fecha_inicio, fecha_fin)` - Consulta BD con filtros
- `obtener_departamentos()` - Obtiene lista de departamentos disponibles
- `obtener_rango_fechas()` - Obtiene rango min/max de fechas
- `normalizar_datos(df)` - Max-Normalization
- `calcular_scores(df)` - AHP score (0-100)
- `asignar_nivel_riesgo(df)` - Clasificación CRÍTICO/ALTO/MEDIO/BAJO
- `analizar(limite, departamento, fecha_inicio, fecha_fin)` - Ejecución completa con filtros

## 🎨 Personalización

Para cambiar la importancia relativa entre Severidad y Frecuencia, modifica en `admin.py`:

```python
analizador = AnalizadorAHP(pairwise_value=5.0)  # Severidad 5x más importante
```

Valores comunes:
- `1.0` = Igual importancia
- `3.0` = Severidad 3x (por defecto)
- `5.0` = Severidad 5x más importante
- `0.5` = Frecuencia 2x más importante

## ⚠️ Troubleshooting

**Error: "No module named pandas"**
```bash
pip install numpy pandas
```

**El gráfico no se muestra:**
- Verifica que hay datos en la BD (empleados con muestras > 0 ppm)
- Abre la consola del navegador (F12) para ver errores de JavaScript

**Datos incorrectos:**
- Limpia la BD y reimporta datos
- Verifica que `MuestraAlcohol.alcohol_ppm` contiene valores válidos

## 📞 Soporte

Para más información sobre la metodología AHP (Analytic Hierarchy Process), consulta la documentación oficial o contacta con el equipo de desarrollo.
