import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from medidor.models import Empleado, MuestraAlcohol


class Command(BaseCommand):
    help = 'Carga datos de empleados y muestras de alcohol desde archivos CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empleados',
            type=str,
            default='empleados.csv',
            help='Ruta del archivo CSV de empleados'
        )
        parser.add_argument(
            '--muestras',
            type=str,
            default='muestras_data.csv',
            help='Ruta del archivo CSV de muestras de alcohol'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        empleados_path = options['empleados']
        muestras_path = options['muestras']

        # Cargar empleados
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Iniciando carga de empleados desde {empleados_path}...'))
        try:
            empleados_cargados = self._cargar_empleados(empleados_path)
            self.stdout.write(self.style.SUCCESS(f'✅ {empleados_cargados} empleados cargados exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al cargar empleados: {str(e)}'))
            return

        # Cargar muestras
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Iniciando carga de muestras desde {muestras_path}...'))
        try:
            muestras_cargadas = self._cargar_muestras(muestras_path)
            self.stdout.write(self.style.SUCCESS(f'✅ {muestras_cargadas} muestras cargadas exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al cargar muestras: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS('\n✨ Carga de datos completada exitosamente'))

    def _cargar_empleados(self, filepath):
        """Carga empleados desde el CSV"""
        empleados_creados = 0

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Verificar si el empleado ya existe
                if Empleado.objects.filter(identificacion=row['identificacion']).exists():
                    self.stdout.write(f'  ⚠️  {row["identificacion"]} ya existe, se omite')
                    continue

                # Parsear fecha
                fecha_ingreso = None
                if row.get('fecha_ingreso'):
                    try:
                        fecha_ingreso = datetime.strptime(row['fecha_ingreso'], '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(f'  ⚠️  Fecha inválida para {row["identificacion"]}: {row["fecha_ingreso"]}')

                # Crear empleado
                empleado = Empleado.objects.create_user(
                    username=row['username'],
                    email=row['email'],
                    password='ChangeMe@123',  # Contraseña temporal; se debe cambiar en admin
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    identificacion=row['identificacion'],
                    departamento=row.get('departamento', 'Sin departamento'),
                    telefono=row.get('telefono', ''),
                    fecha_ingreso=fecha_ingreso
                )
                empleados_creados += 1
                self.stdout.write(f'  ✓ {row["identificacion"]}: {row["first_name"]} {row["last_name"]}')

        return empleados_creados

    def _cargar_muestras(self, filepath):
        """Carga muestras de alcohol desde el CSV"""
        muestras_cargadas = 0
        errores = []

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader, start=2):  # start=2 para contar desde la fila 2 (header es fila 1)
                try:
                    # Obtener empleado por identificacion
                    empleado = Empleado.objects.get(identificacion=row['empleado_identificacion'])

                    # Parsear fecha
                    fecha = datetime.strptime(row['fecha'], '%Y-%m-%d %H:%M:%S')

                    # Crear muestra
                    muestra = MuestraAlcohol.objects.create(
                        empleado=empleado,
                        valor_analogico=int(row['valor_analogico']),
                        voltaje=float(row['voltaje']),
                        alcohol_ppm=float(row['alcohol_ppm']),
                        fecha=fecha
                    )
                    muestras_cargadas += 1

                    # Mostrar progreso cada 50 muestras
                    if muestras_cargadas % 50 == 0:
                        self.stdout.write(f'  ✓ {muestras_cargadas} muestras procesadas...')

                except Empleado.DoesNotExist:
                    errores.append(f'Fila {idx}: Empleado {row["empleado_identificacion"]} no encontrado')
                except ValueError as e:
                    errores.append(f'Fila {idx}: Error al parsear datos - {str(e)}')
                except Exception as e:
                    errores.append(f'Fila {idx}: Error inesperado - {str(e)}')

        # Mostrar resumen de errores
        if errores:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Se encontraron {len(errores)} errores:'))
            for error in errores[:10]:  # Mostrar primeros 10 errores
                self.stdout.write(f'  {error}')
            if len(errores) > 10:
                self.stdout.write(f'  ... y {len(errores) - 10} más')

        return muestras_cargadas
