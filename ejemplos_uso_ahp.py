"""
EJEMPLOS DE USO - Sistema AHP de Análisis de Riesgos de Alcohol

Este script muestra cómo interactuar con el sistema AHP desde Python
"""

# ============================================================================
# 1. EJECUTAR ANÁLISIS COMPLETO
# ============================================================================

from medidor.analisis_ahp import AnalizadorAHP
from medidor.models import CriterioAHP, CalificacionEmpleado, Empleado

# Crear analizador
analizador = AnalizadorAHP()

# Analizar todos los empleados
print("🔄 Ejecutando análisis AHP completo...")
resultados = analizador.analizar_todos_empleados()
print(f"✅ {len(resultados)} empleados analizados")


# ============================================================================
# 2. VER RANKING DE EMPLEADOS
# ============================================================================

print("\n📊 Top 10 empleados por riesgo:")
print("-" * 70)

ranking = AnalizadorAHP.obtener_ranking_empleados(limite=10, ordenar_por='riesgo')

for i, cal in enumerate(ranking, 1):
    print(f"{i:2d}. {cal.empleado.identificacion:10s} | "
          f"{cal.nivel_riesgo:8s} | "
          f"Puntuación: {cal.puntuacion_total:6.2f}% | "
          f"Promedio: {cal.promedio_alcohol_ppm:6.2f} ppm")


# ============================================================================
# 3. OBTENER ESTADÍSTICAS GENERALES
# ============================================================================

print("\n📈 Estadísticas generales:")
print("-" * 70)

stats = AnalizadorAHP.obtener_estadisticas_generales()

if stats:
    print(f"Total de empleados: {stats['total_empleados']}")
    print(f"Puntuación promedio: {stats['promedio_puntuacion']:.2f}%")
    print(f"Puntuación máxima: {stats['max_puntuacion']:.2f}%")
    print(f"\nDistribución por riesgo:")
    print(f"  • Crítico: {stats['conteo_por_riesgo']['CRITICO']}")
    print(f"  • Alto: {stats['conteo_por_riesgo']['ALTO']}")
    print(f"  • Medio: {stats['conteo_por_riesgo']['MEDIO']}")
    print(f"  • Bajo: {stats['conteo_por_riesgo']['BAJO']}")


# ============================================================================
# 4. VER CALIFICACIÓN DE UN EMPLEADO ESPECÍFICO
# ============================================================================

print("\n👤 Calificación detallada de un empleado:")
print("-" * 70)

empleado = Empleado.objects.get(identificacion='EMP001')
calificacion = CalificacionEmpleado.objects.get(empleado=empleado)

print(f"Empleado: {empleado.nombre} ({empleado.identificacion})")
print(f"Departamento: {empleado.departamento}")
print(f"")
print(f"Puntuación AHP: {calificacion.puntuacion_total}%")
print(f"Nivel de Riesgo: {calificacion.get_nivel_riesgo_display()}")
print(f"")
print(f"Métricas:")
print(f"  • Promedio PPM: {calificacion.promedio_alcohol_ppm}")
print(f"  • Máximo PPM: {calificacion.maximo_alcohol_ppm}")
print(f"  • Frecuencia: {calificacion.frecuencia_mediciones} muestras/día")
print(f"  • Variabilidad: {calificacion.indice_variabilidad}")
print(f"  • Total Muestras: {calificacion.numero_muestras}")


# ============================================================================
# 5. VISUALIZAR CRITERIOS AHP ACTIVOS
# ============================================================================

print("\n⚙️  Criterios AHP activos:")
print("-" * 70)

criterios = CriterioAHP.objects.filter(activo=True).order_by('-peso')
peso_total = sum(c.peso for c in criterios) or 1.0

for criterio in criterios:
    peso_norm = (criterio.peso / peso_total) * 100
    print(f"{criterio.nombre:25s} | "
          f"Peso: {criterio.peso:4.2f} | "
          f"Normalizado: {peso_norm:5.1f}% | "
          f"{criterio.descripcion}")


# ============================================================================
# 6. CAMBIAR PESOS DE CRITERIOS Y RECALCULAR
# ============================================================================

print("\n🔧 Ejemplo: Cambiar pesos")
print("-" * 70)
print("Antes:")
for c in CriterioAHP.objects.filter(activo=True):
    print(f"  {c.nombre}: {c.peso}")

# Cambiar pesos (ejemplo: dar más importancia a máximo)
CriterioAHP.objects.filter(nombre='Máximo de Alcohol').update(peso=0.50)
CriterioAHP.objects.filter(nombre='Promedio de Alcohol').update(peso=0.30)

print("\nDespués:")
for c in CriterioAHP.objects.filter(activo=True):
    print(f"  {c.nombre}: {c.peso}")

# Recalcular
print("\n⏳ Recalculando...")
analizador = AnalizadorAHP()  # Reinicializar con nuevos pesos
analizador.analizar_todos_empleados()
print("✅ Análisis actualizado")


# ============================================================================
# 7. FILTRAR EMPLEADOS POR NIVEL DE RIESGO
# ============================================================================

print("\n🚨 Empleados en RIESGO CRÍTICO:")
print("-" * 70)

criticos = CalificacionEmpleado.objects.filter(nivel_riesgo='CRITICO')[:5]

for cal in criticos:
    print(f"{cal.empleado.identificacion:10s} | "
          f"Puntuación: {cal.puntuacion_total:6.2f}% | "
          f"Máximo: {cal.maximo_alcohol_ppm} ppm")


# ============================================================================
# 8. EXPORTAR DATOS PARA ANÁLISIS
# ============================================================================

print("\n📊 Exportar datos para análisis externo:")
print("-" * 70)

import json

# Convertir a JSON
datos_export = []
for cal in CalificacionEmpleado.objects.all()[:10]:
    datos_export.append({
        'empleado_id': cal.empleado.identificacion,
        'nombre': cal.empleado.nombre,
        'departamento': cal.empleado.departamento,
        'puntuacion': cal.puntuacion_total,
        'nivel_riesgo': cal.nivel_riesgo,
        'promedio_ppm': cal.promedio_alcohol_ppm,
        'maximo_ppm': cal.maximo_alcohol_ppm,
        'muestras': cal.numero_muestras,
    })

print(json.dumps(datos_export, indent=2, ensure_ascii=False))


# ============================================================================
# 9. MONITOREO CONTINUO
# ============================================================================

print("\n📡 Monitoreo continuo:")
print("-" * 70)

# Este código puede ejecutarse periódicamente (ej. cada día)
from django.utils import timezone

# Recalcular
analizador.analizar_todos_empleados()

# Ver cambios
cambios_criticio = CalificacionEmpleado.objects.filter(
    nivel_riesgo='CRITICO'
).count()

cambios_alto = CalificacionEmpleado.objects.filter(
    nivel_riesgo='ALTO'
).count()

print(f"Última actualización: {timezone.now()}")
print(f"Empleados en riesgo crítico: {cambios_criticio}")
print(f"Empleados en riesgo alto: {cambios_alto}")

# Alertar si hay cambios significativos
if cambios_criticio > 0:
    print("⚠️  ALERTA: Hay empleados con riesgo CRÍTICO")


# ============================================================================
# 10. COMPARATIVA ANTES/DESPUÉS
# ============================================================================

print("\n📉 Comparativa de empleado en el tiempo:")
print("-" * 70)

# Simular análisis en diferentes momentos
empleado = Empleado.objects.first()
if empleado:
    cal_actual = CalificacionEmpleado.objects.get(empleado=empleado)
    
    print(f"Empleado: {empleado.nombre}")
    print(f"Puntuación actual: {cal_actual.puntuacion_total}%")
    print(f"Nivel actual: {cal_actual.get_nivel_riesgo_display()}")
    print(f"")
    print("Para hacer seguimiento:")
    print("1. Guardar puntuación en fecha")
    print("2. Después de algunas semanas, recalcular")
    print("3. Comparar cambios")
    print("4. Validar efectividad de intervenciones")

print("\n✨ Fin de ejemplos")
