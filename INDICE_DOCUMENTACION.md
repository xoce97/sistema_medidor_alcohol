# 📚 Índice de Documentación - Sistema Medidor Alcohol

## 📋 Estructura de Archivos

```
sistema_medidor_alcohol/
├── 📄 README.md                          (Principal)
├── 📄 RESUMEN_ENTREGA.md                (Resumen ejecutivo final)
│
├── 📄 AHP_ANALISIS_README.md            (Análisis AHP - Teoría)
├── 📄 IMPLEMENTACION_AHP.md             (Implementación AHP - Técnico)
├── 📄 ejemplos_uso_ahp.py              (Ejemplos de uso AHP)
│
├── 📄 ADMIN_DASHBOARD_GUIA.md           (Guía de usuario - Dashboard)
├── 📄 ADMIN_DASHBOARD_RESUMEN.md        (Resumen técnico - Dashboard)
├── 📄 GUIA_DE_PRUEBAS.md                (Test cases y verificaciones)
├── 📄 ESTA_DOCUMENTACION.md             (Índice - Este archivo)
│
├── alcoholimetro2025/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── alcoholimetro2025/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   └── medidor/
│       ├── models.py                   (4 modelos)
│       ├── views.py                    (9 vistas)
│       ├── urls.py                     (11 rutas)
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── tests.py
│       │
│       ├── analisis_ahp.py             (Clase AnalizadorAHP)
│       │
│       ├── management/commands/
│       │   ├── cargar_datos_csv.py    (Carga de datos)
│       │   └── analizar_ahp.py        (Análisis AHP)
│       │
│       ├── migrations/
│       │   ├── 0001_initial.py
│       │   └── 0002_criterioahp_calificacionempleado.py
│       │
│       ├── static/js/
│       │   └── controlMedicion.js
│       │
│       └── templates/
│           ├── base.html
│           ├── inicio.html
│           ├── login.html
│           ├── index.html                (Antes: dashboard.html)
│           ├── reporte_riesgos.html
│           ├── detalle_empleado.html
│           ├── criterios_ahp.html
│           └── admin_dashboard.html      (✨ NUEVO)
│
├── empleados.csv                         (102 registros)
├── muestras_data.csv                     (100,021 registros)
├── ClienteSensor.ino                     (Arduino)
└── alcoholimetro-env-win/                (Entorno virtual)
```

---

## 📖 Guías por Tema

### 🎯 Para Comenzar
1. **[README.md](./README.md)** - Descripción general del proyecto
2. **[RESUMEN_ENTREGA.md](./RESUMEN_ENTREGA.md)** - Estado actual y logros

### 📊 Análisis de Requisitos
1. **[RESUMEN_ENTREGA.md](./RESUMEN_ENTREGA.md)** - Sección "Requisitos del Sistema"
   - Usuarios y roles
   - Casos de uso
   - Especificaciones técnicas

### 🧮 Sistema de Calificación AHP
1. **[AHP_ANALISIS_README.md](./AHP_ANALISIS_README.md)** 
   - Teoría del Analytic Hierarchy Process
   - Criterios utilizados (35% promedio, 35% máximo, etc.)
   - Niveles de riesgo
   
2. **[IMPLEMENTACION_AHP.md](./IMPLEMENTACION_AHP.md)**
   - Detalles técnicos de implementación
   - Clases y métodos
   - Ejemplos de código
   
3. **[ejemplos_uso_ahp.py](./ejemplos_uso_ahp.py)**
   - Scripts de ejemplo
   - Cómo usar AnalizadorAHP
   - Consultas de datos

### 📊 Dashboard Administrativo (✨ NUEVO)
1. **[ADMIN_DASHBOARD_GUIA.md](./ADMIN_DASHBOARD_GUIA.md)**
   - Guía de usuario final
   - Cómo acceder y usar
   - Descripción de features
   
2. **[ADMIN_DASHBOARD_RESUMEN.md](./ADMIN_DASHBOARD_RESUMEN.md)**
   - Resumen técnico
   - Arquitectura
   - Componentes implementados
   
3. **[GUIA_DE_PRUEBAS.md](./GUIA_DE_PRUEBAS.md)**
   - Test cases
   - Verificaciones
   - Troubleshooting

### 💾 Base de Datos
- **Modelos**: `alcoholimetro2025/medidor/models.py`
  - `Empleado` (Django AbstractUser)
  - `MuestraAlcohol` (Mediciones)
  - `CriterioAHP` (Criterios de evaluación)
  - `CalificacionEmpleado` (Puntuaciones)

### 🌐 Rutas y Vistas
- **URLs**: `alcoholimetro2025/medidor/urls.py`
- **Views**: `alcoholimetro2025/medidor/views.py`

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/` | inicio_view | Página principal |
| `/login/` | CustomLoginView | Autenticación |
| `/index/` | index_view | Dashboard personal |
| `/reporte-riesgos/` | reporte_riesgos_view | Reporte de riesgos |
| `/empleado/<id>/` | detalle_empleado_view | Detalle empleado |
| `/criterios-ahp/` | criterios_ahp_view | Criterios AHP |
| `/admin-dashboard/` | admin_dashboard_view | **Dashboard Admin (NUEVO)** |

### 🎨 Templates
- **Base**: `base.html` (Extensión para todas)
- **Públicas**: `inicio.html`, `login.html`
- **Usuario**: `index.html` (Dashboard personal)
- **AHP**: `reporte_riesgos.html`, `detalle_empleado.html`, `criterios_ahp.html`
- **Admin**: `admin_dashboard.html` ✨ **NUEVO**

---

## 🚀 Guías de Ejecución

### Cargar Datos Iniciales
```bash
python manage.py cargar_datos_csv
```
**Resultado**: 102 empleados + 100,021 muestras

### Ejecutar Análisis AHP
```bash
python manage.py analizar_ahp --inicializar-criterios --mostrar-stats
```
**Resultado**: CalificacionEmpleado creadas para 101 empleados

### Iniciar Servidor
```bash
python manage.py runserver
```
**URL**: http://127.0.0.1:8000/

### Acceder a Dashboard Admin
```
http://127.0.0.1:8000/admin-dashboard/
(Requiere usuario admin)
```

---

## 📊 Componentes Principales

### 1. Modelo de Datos
```
Empleado
├── identificacion (PK)
├── nombre
├── departamento
├── email
└── ... (heredado de AbstractUser)

MuestraAlcohol
├── id (PK)
├── empleado (FK)
├── fecha
├── valor_analogico
├── voltaje
└── alcohol_ppm

CriterioAHP
├── id (PK)
├── nombre
├── descripcion
├── peso (0-1)
└── activo

CalificacionEmpleado
├── id (PK)
├── empleado (OneToOne)
├── puntuacion_total (0-100%)
├── nivel_riesgo (ENUM)
├── promedio_alcohol_ppm
├── maximo_alcohol_ppm
├── frecuencia_mediciones
├── indice_variabilidad
└── numero_muestras
```

### 2. Algoritmo AHP
```python
AnalizadorAHP
├── __init__()
├── normalizar_criterios()          # Pesos normalizados
├── normalizar_valor()              # Min-max scaling
├── calcular_calificacion()         # Puntuación 0-100%
├── determinar_nivel_riesgo()       # BAJO/MEDIO/ALTO/CRÍTICO
├── analizar_todos_empleados()      # Bulk analysis
├── obtener_ranking_empleados()     # Top 10
└── obtener_estadisticas_generales() # Agregados
```

### 3. Vistas (Views)
```python
Views Disponibles:
├── inicio_view()                   # Pública
├── index_view()                    # Personal dashboard
├── reporte_riesgos_view()          # Reporte completo
├── detalle_empleado_view()         # Detalle por empleado
├── criterios_ahp_view()            # Información de criterios
└── admin_dashboard_view()          # 🆕 Dashboard administrativo
```

### 4. Templates
```
Jerarquía:
base.html
├── inicio.html
├── login.html
├── index.html
├── reporte_riesgos.html
├── detalle_empleado.html
├── criterios_ahp.html
└── admin_dashboard.html (🆕)
```

---

## 🔒 Seguridad Implementada

### Control de Acceso
- ✅ `@login_required` en vistas protegidas
- ✅ `is_staff` para dashboard admin
- ✅ CSRF protection en forms
- ✅ SQL injection prevention (ORM)

### Permisos
- 📝 Usuario regular: Ver su propio dashboard
- 📊 Usuario admin: Ver dashboard administrativo
- 🔑 Superuser: Acceso completo

---

## 📈 Estadísticas del Sistema

### Datos Cargados
```
Empleados:           102
Muestras:           100,021
Empleados Analizados: 101
Criterios AHP:        4
Período de Datos:     ~30 días
```

### Distribución de Riesgo
```
Riesgo BAJO:        58 empleados (57.43%)
Riesgo MEDIO:       28 empleados (27.72%)
Riesgo ALTO:        12 empleados (11.88%)
Riesgo CRÍTICO:      3 empleados (2.97%)
```

### Métricas Promedio
```
Puntuación Promedio:    45.32%
Alcohol Máximo:         ~100 ppm
Alcohol Promedio:       ~50 ppm
Muestras/Empleado:      ~1000
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.8** - Framework web
- **Python 3.10** - Lenguaje
- **SQLite** - Base de datos
- **Chart.js 3.9.1** - Gráficos (frontend)

### Frontend
- **Bootstrap 5** - CSS framework
- **HTML5** - Estructura
- **JavaScript** - Interactividad
- **Chart.js** - Visualización

### Herramientas
- **Git** - Control de versión
- **Django ORM** - Acceso a datos
- **Django Templates** - Templating
- **Django Migrations** - Versionado DB

---

## 📝 Documentos por Fase

### Fase 1: Análisis de Requisitos
- IEEE 830 SRS (en RESUMEN_ENTREGA.md)
- Especificaciones técnicas

### Fase 2: Carga de Datos
- Management command: `cargar_datos_csv.py`
- 102 empleados importados
- 100,021 muestras importadas

### Fase 3: Sistema de Análisis
- Implementación AHP
- Modelo `CriterioAHP` y `CalificacionEmpleado`
- Clase `AnalizadorAHP`

### Fase 4: Vistas y Reportes
- 3 vistas AHP
- 3 templates AHP
- Reporte de riesgos

### Fase 5: Dashboard Administrativo (✨ ACTUAL)
- Vista: `admin_dashboard_view()`
- Template: `admin_dashboard.html`
- Selector de empleados
- Gráfico Chart.js
- Estadísticas
- Tablas

---

## 🎓 Cómo Usar Esta Documentación

### Si eres Usuario Final
→ Lee: **[ADMIN_DASHBOARD_GUIA.md](./ADMIN_DASHBOARD_GUIA.md)**

### Si eres Desarrollador
→ Lee: **[ADMIN_DASHBOARD_RESUMEN.md](./ADMIN_DASHBOARD_RESUMEN.md)** y código fuente

### Si necesitas Hacer Pruebas
→ Lee: **[GUIA_DE_PRUEBAS.md](./GUIA_DE_PRUEBAS.md)**

### Si necesitas Entender AHP
→ Lee: **[AHP_ANALISIS_README.md](./AHP_ANALISIS_README.md)**

### Si necesitas Implementar AHP
→ Lee: **[IMPLEMENTACION_AHP.md](./IMPLEMENTACION_AHP.md)**

### Si necesitas Ejemplos de Código
→ Lee: **[ejemplos_uso_ahp.py](./ejemplos_uso_ahp.py)**

---

## 🔗 Enlaces Rápidos

### Código Fuente
- [models.py](./alcoholimetro2025/medidor/models.py) - Modelos
- [views.py](./alcoholimetro2025/medidor/views.py) - Vistas
- [urls.py](./alcoholimetro2025/medidor/urls.py) - Rutas
- [analisis_ahp.py](./alcoholimetro2025/medidor/analisis_ahp.py) - AHP
- [admin_dashboard.html](./alcoholimetro2025/medidor/templates/admin_dashboard.html) - Template

### Comandos
- [cargar_datos_csv.py](./alcoholimetro2025/medidor/management/commands/cargar_datos_csv.py)
- [analizar_ahp.py](./alcoholimetro2025/medidor/management/commands/analizar_ahp.py)

### Datos
- [empleados.csv](./empleados.csv)
- [muestras_data.csv](./muestras_data.csv)

---

## 🚨 FAQ

### ¿Cómo accedo al dashboard admin?
1. Crea usuario con `is_staff=True`
2. Accede a `/admin-dashboard/`
3. Selecciona un empleado

### ¿Cómo interpreto la puntuación AHP?
- 0-50%: Bajo riesgo ✅
- 50-75%: Medio riesgo ⚠️
- 75-100%: Alto riesgo ❌
- O máximo ≥ 100 ppm: Crítico 🚨

### ¿Cómo recalculo los análisis?
```bash
python manage.py analizar_ahp
```

### ¿Dónde están los datos?
```bash
# Base de datos
db.sqlite3

# CSVs originales
empleados.csv
muestras_data.csv
```

### ¿Cómo cambio los criterios AHP?
Editar en Django admin o código en `analizar_ahp.py`

---

## 📞 Soporte

### Problemas Comunes
- **Error 403**: Usuario no es admin
- **No hay datos**: Ejecutar `cargar_datos_csv`
- **Gráfico no aparece**: Verificar datos del empleado
- **Template error**: Verificar Chart.js CDN

### Recursos Útiles
- [Django Documentation](https://docs.djangoproject.com/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Bootstrap Documentation](https://getbootstrap.com/)

---

## ✅ Checklist de Proyecto

- [x] Análisis de requisitos (IEEE 830 SRS)
- [x] Diseño de base de datos
- [x] Carga de datos CSV
- [x] Implementación de AHP
- [x] Vistas de reporte
- [x] Dashboard de usuario
- [x] Dashboard administrativo ✨
- [ ] Tests automatizados
- [ ] Documentación de API
- [ ] Deployment

---

## 📊 Estadísticas de Documentación

```
Documentos Markdown:    8+
Archivos de Código:    20+
Líneas de Código:     1000+
Líneas de Docs:      2000+
Modelos Django:         4
Vistas Django:          9
Rutas:                 11
Templates:              8
Management Commands:    2
```

---

**Fecha de Actualización**: Diciembre 2024
**Versión**: 1.0
**Estado**: ✅ Completo y Operativo
**Próxima Fase**: Testing automatizado y deployment

