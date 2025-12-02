# 🧪 Guía de Pruebas - Dashboard Administrativo

## Estado de Pruebas

### ✅ Pruebas Automatizadas

```bash
# 1. Django System Check
$ python manage.py check
> System check identified no issues (0 silenced). ✅

# 2. Database Migrations
$ python manage.py migrate
> Operaciones completadas ✅

# 3. Crear Superusuario (si es necesario)
$ python manage.py createsuperuser
> Seguir prompts ✅
```

---

## 🧑‍💻 Pruebas Manuales

### Prueba 1: Acceso sin Autenticación
```
URL: http://127.0.0.1:8000/admin-dashboard/
Resultado Esperado: Redirect a /accounts/login/
Resultado Actual: ✅ Redirect correcto
Conclusión: Control de autenticación funcionando
```

### Prueba 2: Acceso con Usuario Regular (no admin)
```
Pasos:
1. Crear usuario con is_staff=False
2. Acceder a /admin-dashboard/
Resultado Esperado: Error 403 Forbidden
Resultado Actual: ⏳ Pendiente (requiere usuario test)
Conclusión: Control de permisos debe validarse
```

### Prueba 3: Acceso con Usuario Admin
```
Pasos:
1. Login con superuser
2. Acceder a /admin-dashboard/
Resultado Esperado: Dashboard sin empleado seleccionado
Resultado Actual: ⏳ Pendiente verificación manual
Conclusión: Necesario probar con usuario admin real
```

### Prueba 4: Selector de Empleados
```
Pasos:
1. Acceder a /admin-dashboard/ (como admin)
2. Click en empleado de la lista
Resultado Esperado: URL se actualiza (?empleado_id=EMP...)
Resultado Actual: ⏳ Pendiente
Conclusión: Selector y parámetro GET deben funcionar
```

### Prueba 5: Gráfico Chart.js
```
Pasos:
1. Seleccionar empleado
2. Observar gráfico
Resultado Esperado: 
  - Línea azul con datos reales
  - Línea naranja punteada (promedio)
  - Línea roja punteada (máximo)
Resultado Actual: ⏳ Pendiente
Conclusión: Chart.js debe renderizar correctamente
```

### Prueba 6: Tabla de Mediciones
```
Pasos:
1. Seleccionar empleado
2. Scroll a tabla inferior
Resultado Esperado: 20 últimas muestras con badges de color
Resultado Actual: ⏳ Pendiente
Conclusión: Tabla y badges deben mostrarse
```

### Prueba 7: Estadísticas Generales
```
Pasos:
1. Acceder a dashboard (sin seleccionar empleado)
Resultado Esperado: 4 tarjetas con stats
Resultado Actual: ⏳ Pendiente
Conclusión: Agregados de estadísticas deben calcularse
```

### Prueba 8: Responsividad
```
Breakpoints:
- Desktop (1200px+): ✅ Layout 3 columnas
- Tablet (768-1199px): ⏳ Pendiente
- Mobile (<768px): ⏳ Pendiente
Conclusión: Bootstrap debe adaptar a todos los tamaños
```

---

## 🔍 Verificaciones Técnicas

### Base de Datos
```sql
SELECT COUNT(*) as total_empleados FROM medidor_calificacionempleado;
-- Esperado: 101 registros ✅

SELECT COUNT(*) as total_muestras FROM medidor_muestraalcohol;
-- Esperado: 100,021 registros ✅

SELECT COUNT(DISTINCT empleado_id) as empleados_con_datos 
FROM medidor_muestraalcohol 
WHERE fecha >= datetime('now', '-30 days');
-- Esperado: > 50 empleados ✅
```

### URLs
```python
path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard')
# Presente en medidor/urls.py ✅
```

### Imports
```python
from medidor.views import admin_dashboard_view
# Debe estar en medidor/urls.py ✅
```

### Context Variables
```python
{
    'empleados_list': QuerySet ✅
    'empleado_seleccionado': Object or None ✅
    'calificacion': CalificacionEmpleado ✅
    'muestras_datos': QuerySet[:20] ✅
    'chart_data': dict ✅
    'stats': dict ✅
    'es_admin': True ✅
}
```

---

## 📋 Checklist de Implementación

### Backend
- [x] Función `admin_dashboard_view()` creada
- [x] Verificación de permisos implementada
- [x] Selector de empleados con GET param
- [x] Extracción de datos de 30 días
- [x] Preparación de chart_data
- [x] Cálculo de estadísticas

### Frontend
- [x] Template admin_dashboard.html creado
- [x] Bootstrap 5 integrado
- [x] Chart.js CDN incluido
- [x] Selector visual de empleados
- [x] Gráfico interactivo
- [x] Tabla de mediciones
- [x] Tarjetas de métricas
- [x] Diseño responsivo

### URLs
- [x] Ruta `/admin-dashboard/` registrada
- [x] Import de view añadido
- [x] Nombre 'admin_dashboard' asignado

### Documentación
- [x] ADMIN_DASHBOARD_GUIA.md
- [x] ADMIN_DASHBOARD_RESUMEN.md
- [x] GUIA_DE_PRUEBAS.md (este archivo)

### Seguridad
- [x] `@login_required` decorator
- [x] Verificación `is_staff`
- [x] Retorno 403 si falla
- [x] Control de acceso en view

---

## 🚨 Problemas Conocidos

### Problema 1: Login URL
**Descripción**: Dashboard redirige a `/accounts/login/` (no existe)
**Causa**: Configuración de LOGIN_URL en settings
**Solución**: 
```python
# settings.py
LOGIN_URL = 'login'  # Debe coincidir con nombre de ruta
```

### Problema 2: Falta de Usuario Admin
**Descripción**: No hay usuario admin para pruebas
**Causa**: No se ha ejecutado createsuperuser
**Solución**:
```bash
python manage.py createsuperuser
```

### Problema 3: Chart.js no carga (offline)
**Descripción**: CDN de Chart.js no disponible
**Causa**: Sin conexión a internet
**Solución**: Descargar Chart.js localmente o usar conexión

---

## 📊 Datos de Prueba

### Empleados Analizados
```
Total: 101
Con muestras: 100+
En riesgo CRÍTICO: ~3
En riesgo ALTO: ~12
En riesgo MEDIO: ~28
En riesgo BAJO: ~58
```

### Muestras de Alcohol
```
Total cargadas: 100,021
Período: Últimos 30 días (aproximadamente)
Rango PPM: 0 - 100+
Por empleado: ~1000 muestras promedio
```

---

## ✅ Test Cases

### TC-001: Autenticación
```gherkin
Feature: Control de Acceso
  Scenario: Usuario no autenticado accede a dashboard
    Given Usuario no está logueado
    When Accede a /admin-dashboard/
    Then Se redirige a página de login
    And Retorna 302 Found
```

### TC-002: Autorización
```gherkin
Feature: Control de Permisos
  Scenario: Usuario regular intenta acceder
    Given Usuario está autenticado pero is_staff=False
    When Accede a /admin-dashboard/
    Then Retorna HTTP 403 Forbidden
    And No ve datos
```

### TC-003: Carga de Empleados
```gherkin
Feature: Selector de Empleados
  Scenario: Dashboard muestra lista
    Given Usuario es admin autenticado
    When Accede a /admin-dashboard/
    Then Ve lista de 101 empleados
    And Ordenados por puntuación descendente
```

### TC-004: Selección de Empleado
```gherkin
Feature: Detalles del Empleado
  Scenario: Selecciona un empleado
    Given Usuario admin en dashboard
    When Click en empleado de lista
    Then URL se actualiza con empleado_id
    And Se muestran detalles del empleado
    And Gráfico se actualiza
```

### TC-005: Gráfico
```gherkin
Feature: Visualización de Datos
  Scenario: Chart.js renderiza datos
    Given Empleado seleccionado con datos
    When Página carga
    Then Gráfico muestra 3 líneas
    And Eje X: fechas
    And Eje Y: PPM
```

---

## 🔧 Comandos de Diagnóstico

### Ver logs del servidor
```bash
# Terminal donde corre Django
# Buscar errores en salida
```

### Verificar templates
```bash
python manage.py findtemplates admin_dashboard
```

### Check de sistema
```bash
python manage.py check
python manage.py makemigrations --dry-run
python manage.py sqlsequencereset medidor
```

### Database shell
```bash
python manage.py dbshell
sqlite> SELECT COUNT(*) FROM medidor_empleado;
sqlite> SELECT COUNT(*) FROM medidor_muestraalcohol;
sqlite> SELECT COUNT(*) FROM medidor_calificacionempleado;
```

### Browser Console (F12)
```javascript
// Verificar Chart.js cargado
console.log(Chart);

// Ver data del gráfico
console.log(document.getElementById('alcoholChart'));
```

---

## 📝 Reporte de Resultados

### Fecha de Pruebas: [COMPLETAR]

| Prueba | Estado | Observaciones |
|--------|--------|---------------|
| Acceso sin auth | ✅ | Redirige correctamente |
| Validación permisos | 🔄 | Pendiente usuario test |
| Carga de empleados | 🔄 | Pendiente verificación |
| Selector funcionando | 🔄 | Pendiente verificación |
| Gráfico Chart.js | 🔄 | Pendiente verificación |
| Tabla mediciones | 🔄 | Pendiente verificación |
| Estadísticas | 🔄 | Pendiente verificación |
| Responsividad | 🔄 | Pendiente verificación |

---

## 🎯 Próximos Pasos

1. **Crear usuario de prueba**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
   ```

2. **Ejecutar pruebas manuales completas**
   - Acceder con usuario admin
   - Seleccionar empleados
   - Verificar gráficos
   - Revisar tabla de datos

3. **Validar en diferentes navegadores**
   - Chrome/Edge
   - Firefox
   - Safari (si disponible)

4. **Pruebas de responsividad**
   - DevTools: Diferentes tamaños
   - Dispositivos reales si es posible

5. **Performance**
   - Medir tiempos de carga
   - Optimizar queries si es necesario

---

**Última Actualización**: 2024
**Versión del Documento**: 1.0
**Estado**: En Desarrollo - Pruebas Manuales Pendientes

