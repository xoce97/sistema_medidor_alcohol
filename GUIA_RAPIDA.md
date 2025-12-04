# Guía Rápida - Sistema AHP de Riesgo de Alcohol

## Estado Actual: ✓ COMPLETAMENTE OPERACIONAL

### Base de Datos
- **77 empleados** cargados
- **1000 muestras** de alcohol registradas
- **7 departamentos** diferentes

### Todos los Endpoints Funcionan
✓ Dashboard General  
✓ Filtros (Departamento, Fechas, Low-Risk)  
✓ Export PDF  
✓ Export CSV  

---

## Acceso Rápido

### 1. Iniciar Servidor
```bash
cd alcoholimetro2025
python manage.py runserver 0.0.0.0:8000
```

### 2. Credenciales
```
Usuario: admin
Contraseña: admin123
```

### 3. URLs
- **Dashboard:** http://localhost:8000/admin/medidor/empleado/dashboard-ahp/
- **Admin Panel:** http://localhost:8000/admin/

---

## Funcionalidades

### Dashboard
- Visualización TOP 10 empleados con mayor riesgo
- Gráfico de barras (AHP Score) + línea (Max PPM)
- Tabla detallada con niveles de riesgo

### Filtros
- **Por Departamento:** Selector dropdown
- **Por Rango de Fechas:** Inputs desde/hasta
- **Orden:** Mayor a Menor Riesgo (default) / Menor a Mayor Riesgo

### Exportaciones
- **PDF:** Tabla formateada
- **CSV:** Datos completos en UTF-8

---

## Niveles de Riesgo (Escala AHP 0-100%)

| Nivel | Rango | Color |
|-------|-------|-------|
| CRÍTICO | ≥ 80% | Rojo |
| ALTO | 60-79% | Naranja |
| MEDIO | 40-59% | Amarillo |
| BAJO | < 40% | Verde |

---

## Datos de Prueba

**Empleados de Alto Riesgo:**
- EMP020: Abraham Pantoja (96.99% - CRÍTICO)
- EMP045: Soledad Regalado (92.22% - CRÍTICO)

---

## Que está Listo

✓ Algoritmo AHP con matriz 2x2  
✓ Cálculo automático de scores  
✓ Dashboard interactivo  
✓ Filtros funcionando  
✓ Exportación a PDF  
✓ Exportación a CSV  
✓ Base de datos sincronizada  
✓ Migrations aplicadas  
✓ Autenticación requerida  

---

## Documentación Completa

Ver: `VALIDACION_SISTEMA.md`

---

**Última actualización:** 4 de Diciembre de 2025
