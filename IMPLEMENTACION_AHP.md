# 📊 Implementación: Modelo AHP para Análisis de Riesgos de Alcohol

## ✅ Componentes Implementados

### 1. Modelos Django (`medidor/models.py`)
```
✓ CriterioAHP
  - nombre: CharField (único)
  - descripcion: TextField
  - peso: FloatField (0-1)
  - activo: BooleanField

✓ CalificacionEmpleado
  - empleado: OneToOneField (Empleado)
  - puntuacion_total: FloatField (0-100%)
  - nivel_riesgo: CharField (BAJO, MEDIO, ALTO, CRÍTICO)
  - promedio_alcohol_ppm: FloatField
  - maximo_alcohol_ppm: FloatField
  - frecuencia_mediciones: FloatField
  - indice_variabilidad: FloatField
  - numero_muestras: IntegerField
```

### 2. Servicio de Análisis (`medidor/analisis_ahp.py`)
```
✓ Clase AnalizadorAHP
  ├─ normalizar_criterios()
  ├─ extraer_metricas_empleado()
  ├─ normalizar_valor() [min-max scaling]
  ├─ calcular_calificacion()
  ├─ determinar_nivel_riesgo()
  ├─ analizar_todos_empleados()
  ├─ obtener_ranking_empleados()
  └─ obtener_estadisticas_generales()
```

### 3. Management Command (`medidor/management/commands/analizar_ahp.py`)
```bash
✓ python manage.py analizar_ahp [opciones]
  --inicializar-criterios  → Crea criterios predeterminados
  --mostrar-stats         → Muestra estadísticas al final
```

### 4. Vistas Django (`medidor/views.py`)
```
✓ reporte_riesgos_view()     → Ranking general de riesgos
✓ detalle_empleado_view()    → Detalles de un empleado
✓ criterios_ahp_view()       → Información de criterios
```

### 5. Rutas URL (`medidor/urls.py`)
```
✓ /reporte-riesgos/         → Tabla con ranking
✓ /empleado/<id>/           → Perfil detallado
✓ /criterios-ahp/           → Documentación del modelo
```

### 6. Templates HTML
```
✓ reporte_riesgos.html      → Estadísticas y ranking
✓ detalle_empleado.html     → Perfil con gráficos
✓ criterios_ahp.html        → Explicación del método
```

---

## 🔄 Flujo de Cálculo AHP

```
┌─────────────────────────────────────────────────────┐
│                  DATOS CRUDOS                       │
│  MuestraAlcohol (ppm, voltaje, valor_analogico)    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              EXTRACCIÓN DE MÉTRICAS                 │
│  • Promedio PPM        (media)                      │
│  • Máximo PPM          (max)                        │
│  • Desv. Estándar      (std)                        │
│  • Frecuencia          (muestras/día)               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         NORMALIZACIÓN GLOBAL (MIN-MAX)              │
│  valor_normalizado = (valor - min) / (max - min)   │
│  Rango: [0, 1]                                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│        APLICACIÓN DE PESOS AHP                      │
│                                                     │
│  Puntuación = Σ(peso_i × valor_i × 100)           │
│                                                     │
│  Promedio:      35% × valor_normalizado × 100      │
│  Máximo:        35% × valor_normalizado × 100      │
│  Frecuencia:    15% × valor_normalizado × 100      │
│  Variabilidad:  15% × valor_normalizado × 100      │
│                 ─────                               │
│  Total:        100%                                 │
│                                                     │
│  Resultado: Puntuación 0-100%                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         CLASIFICACIÓN DE RIESGO                     │
│                                                     │
│  IF máximo_ppm >= 100       → CRÍTICO              │
│  ELSE IF puntuación >= 75   → ALTO                 │
│  ELSE IF puntuación >= 50   → MEDIO                │
│  ELSE                       → BAJO                 │
└─────────────────────────────────────────────────────┘
```

---

## 📈 Criterios AHP (Predeterminados)

| Criterio | Descripción | Peso | % Normalizado |
|----------|-------------|------|---------------|
| 🔴 Promedio de Alcohol | Promedio de ppm detectados | 0.35 | **35%** |
| 🔴 Máximo de Alcohol | Valor pico registrado | 0.35 | **35%** |
| 🟡 Frecuencia | Muestras por día | 0.15 | **15%** |
| 🔵 Variabilidad | Desv. estándar | 0.15 | **15%** |
| | **TOTAL** | **1.0** | **100%** |

---

## 🎯 Niveles de Riesgo

```
┌────────────────────────────────────────────┐
│  Clasificación Automática                  │
├────────────────────────────────────────────┤
│  🟢 BAJO      │ Puntuación < 50%           │
│               │ Y Promedio < 50 ppm        │
├────────────────────────────────────────────┤
│  🔵 MEDIO     │ Puntuación 50-75%          │
│               │ O Promedio 50-80 ppm       │
├────────────────────────────────────────────┤
│  🟡 ALTO      │ Puntuación > 75%           │
│               │ O Promedio > 80 ppm        │
├────────────────────────────────────────────┤
│  🔴 CRÍTICO   │ Máximo > 100 ppm           │
│               │ (Independiente de others)  │
└────────────────────────────────────────────┘
```

---

## 🚀 Uso Rápido

### Inicializar
```bash
cd alcoholimetro2025
..\alcoholimetro-env-win\Scripts\python manage.py analizar_ahp --inicializar-criterios --mostrar-stats
```

### Ver Reportes
1. Inicia sesión en la aplicación web
2. Accede a: `/reporte-riesgos/`
3. Haz clic en un empleado para ver detalles
4. Ve a `/criterios-ahp/` para entender el modelo

### Ajustar Criterios
```bash
python manage.py createsuperuser  # Si es necesario
# Accede a http://localhost:8000/admin/
# Edita CriterioAHP y ajusta pesos
python manage.py analizar_ahp  # Recalcula
```

---

## 📊 Resultado del Análisis Actual

```
✅ Análisis completado
   • 101 empleados analizados

📊 Top 10 empleados por riesgo:

   1. EMP097     | CRITICO  | Puntuación:  75.46% | Promedio: 750.51 ppm
   2. EMP099     | CRITICO  | Puntuación:  56.71% | Promedio:  54.06 ppm
   3. EMP087     | CRITICO  | Puntuación:  56.66% | Promedio:  54.71 ppm
   4. EMP094     | CRITICO  | Puntuación:  56.16% | Promedio:  51.97 ppm
   5. EMP059     | CRITICO  | Puntuación:  56.12% | Promedio:  52.62 ppm
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

---

## 🔧 Personalización

### Cambiar Pesos
```python
# En la base de datos
CriterioAHP.objects.filter(nombre='Promedio de Alcohol').update(peso=0.40)
CriterioAHP.objects.filter(nombre='Máximo de Alcohol').update(peso=0.40)
CriterioAHP.objects.filter(nombre='Frecuencia de Mediciones').update(peso=0.10)
CriterioAHP.objects.filter(nombre='Variabilidad').update(peso=0.10)
```

### Agregar Nuevo Criterio
```python
from medidor.models import CriterioAHP

CriterioAHP.objects.create(
    nombre='Consistencia',
    descripcion='Mediciones consistentes en el tiempo',
    peso=0.20,
    activo=True
)
```

### Cambiar Umbrales de Riesgo
Edita el método `determinar_nivel_riesgo()` en `medidor/analisis_ahp.py`

---

## 📁 Estructura de Archivos

```
medidor/
├── models.py                    ← CriterioAHP, CalificacionEmpleado
├── views.py                     ← 3 nuevas vistas AHP
├── urls.py                      ← 3 nuevas rutas
├── analisis_ahp.py              ← Servicio AnalizadorAHP (principal)
├── management/commands/
│   └── analizar_ahp.py          ← Management command
├── templates/
│   ├── reporte_riesgos.html     ← Ranking general
│   ├── detalle_empleado.html    ← Perfil individual
│   └── criterios_ahp.html       ← Documentación
└── migrations/
    └── 0002_criterioahp_calificacionempleado.py
```

---

## ✨ Características Avanzadas

- ✅ Normalización global (comparación con máximos de todos)
- ✅ Pesos automáticamente normalizados
- ✅ Clasificación inteligente multi-factor
- ✅ Persistencia de resultados
- ✅ Ranking ordenable
- ✅ Estadísticas agregadas
- ✅ Interfaz web responsive
- ✅ Exportable a reportes

---

## 🔮 Próximas Fases

1. **API REST** - Endpoints JSON para programas externos
2. **Gráficos** - Visualización con Chart.js
3. **Exportación** - PDF, Excel, CSV
4. **Historiales** - Versionado de análisis
5. **Alertas** - Notificaciones por cambio de riesgo
6. **Configuración por Departamento** - Umbrales personalizados
7. **Matriz AHP** - Interfaz para calibrar pesos participativamente

---

## 📞 Soporte

Para preguntas sobre el modelo AHP:
- Documentación: `/criterios-ahp/`
- Archivo: `AHP_ANALISIS_README.md`
- Código: `medidor/analisis_ahp.py`
