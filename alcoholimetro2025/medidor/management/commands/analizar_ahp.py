"""
Management command para ejecutar análisis AHP de empleados
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from medidor.analisis_ahp import AnalizadorAHP
from medidor.models import CriterioAHP


class Command(BaseCommand):
    help = 'Ejecuta análisis AHP y genera calificaciones de empleados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--inicializar-criterios',
            action='store_true',
            help='Crea los criterios AHP predeterminados'
        )
        parser.add_argument(
            '--mostrar-stats',
            action='store_true',
            help='Muestra estadísticas generales después del análisis'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['inicializar_criterios']:
            self.stdout.write(self.style.SUCCESS('\n🔄 Inicializando criterios AHP...'))
            self._inicializar_criterios()
        
        self.stdout.write(self.style.SUCCESS('\n🔄 Ejecutando análisis AHP...'))
        analizador = AnalizadorAHP()
        
        resultados = analizador.analizar_todos_empleados()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Análisis completado'))
        self.stdout.write(f'   • {len(resultados)} empleados analizados\n')
        
        # Mostrar ranking
        self.stdout.write(self.style.SUCCESS('📊 Top 10 empleados por riesgo:\n'))
        ranking = AnalizadorAHP.obtener_ranking_empleados(limite=10, ordenar_por='riesgo')
        
        for i, cal in enumerate(ranking, 1):
            color_map = {
                'CRITICO': self.style.ERROR,
                'ALTO': self.style.WARNING,
                'MEDIO': self.style.HTTP_INFO,
                'BAJO': self.style.SUCCESS,
            }
            colorizer = color_map.get(cal.nivel_riesgo, self.style.HTTP_INFO)
            
            self.stdout.write(
                f'  {i:2d}. {colorizer(f"{cal.empleado.identificacion:10s} | "
                f"{cal.nivel_riesgo:8s} | Puntuación: {cal.puntuacion_total:6.2f}% | "
                f"Promedio: {cal.promedio_alcohol_ppm:6.2f} ppm")}'
            )
        
        # Mostrar estadísticas
        if options['mostrar_stats']:
            stats = AnalizadorAHP.obtener_estadisticas_generales()
            if stats:
                self.stdout.write(self.style.SUCCESS('\n📈 Estadísticas generales:\n'))
                self.stdout.write(f'   • Total de empleados: {stats["total_empleados"]}')
                self.stdout.write(f'   • Puntuación promedio: {stats["promedio_puntuacion"]:.2f}%')
                self.stdout.write(f'   • Puntuación máxima: {stats["max_puntuacion"]:.2f}%')
                self.stdout.write(f'\n   Distribución por riesgo:')
                self.stdout.write(f'   • Crítico: {stats["conteo_por_riesgo"]["CRITICO"]}')
                self.stdout.write(f'   • Alto: {stats["conteo_por_riesgo"]["ALTO"]}')
                self.stdout.write(f'   • Medio: {stats["conteo_por_riesgo"]["MEDIO"]}')
                self.stdout.write(f'   • Bajo: {stats["conteo_por_riesgo"]["BAJO"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✨ Análisis AHP completado exitosamente\n'))

    def _inicializar_criterios(self):
        """Crea los criterios AHP predeterminados"""
        criterios_predeterminados = [
            {
                'nombre': 'Promedio de Alcohol',
                'descripcion': 'Promedio de ppm de alcohol detectados en mediciones',
                'peso': 0.35,
            },
            {
                'nombre': 'Máximo de Alcohol',
                'descripcion': 'Valor máximo de ppm alcanzado',
                'peso': 0.35,
            },
            {
                'nombre': 'Frecuencia de Mediciones',
                'descripcion': 'Cantidad de mediciones realizadas',
                'peso': 0.15,
            },
            {
                'nombre': 'Variabilidad',
                'descripcion': 'Desviación estándar en los niveles de alcohol',
                'peso': 0.15,
            },
        ]
        
        for criterio_data in criterios_predeterminados:
            criterio, created = CriterioAHP.objects.get_or_create(
                nombre=criterio_data['nombre'],
                defaults={
                    'descripcion': criterio_data['descripcion'],
                    'peso': criterio_data['peso'],
                    'activo': True,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ {criterio_data["nombre"]} creado (peso: {criterio_data["peso"]})')
            else:
                self.stdout.write(f'  ⚠️  {criterio_data["nombre"]} ya existe')
