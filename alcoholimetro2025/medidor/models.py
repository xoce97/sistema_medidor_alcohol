from django.db import models
from django.contrib.auth.models import AbstractUser


class Empleado(AbstractUser):
    # Campos heredados (username, first_name, last_name, email, password, etc.)
    identificacion = models.CharField(max_length=20, unique=True)
    departamento = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)

    # Metadata
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['identificacion', 'email', 'first_name', 'last_name']

    # Propiedad para compatibilidad
    @property
    def nombre(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"
    
     # Método adicional para obtener el ID de empleado consistente
    @property
    def empleado_id(self):
        """Devuelve la identificación como string o el ID según prefieras"""
        return str(self.identificacion)  # o str(self.id) si prefieres usar el ID numérico

class MuestraAlcohol(models.Model):
    empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='muestras', to_field='identificacion'  # ¡Clave para mantener relaciones existentes!
    )
    valor_analogico = models.IntegerField()
    voltaje = models.FloatField()
    alcohol_ppm = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Muestra de Alcohol'
        verbose_name_plural = 'Muestras de Alcohol'

    def __str__(self):
        return f"{self.empleado.identificacion} - {self.alcohol_ppm}ppm ({self.fecha.date()})"


class CriterioAHP(models.Model):
    """Modelo para almacenar criterios de análisis AHP"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    peso = models.FloatField(default=1.0, help_text="Peso del criterio (0-1)")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-peso']
        verbose_name = 'Criterio AHP'
        verbose_name_plural = 'Criterios AHP'

    def __str__(self):
        return f"{self.nombre} (peso: {self.peso})"


class CalificacionEmpleado(models.Model):
    """Modelo para almacenar calificaciones finales de empleados basadas en AHP"""
    NIVEL_RIESGO_CHOICES = [
        ('BAJO', 'Bajo Riesgo'),
        ('MEDIO', 'Medio Riesgo'),
        ('ALTO', 'Alto Riesgo'),
        ('CRITICO', 'Crítico'),
    ]

    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, related_name='calificacion')
    puntuacion_total = models.FloatField(help_text="Puntuación AHP normalizada (0-100)")
    nivel_riesgo = models.CharField(max_length=20, choices=NIVEL_RIESGO_CHOICES)
    
    # Componentes de la calificación
    promedio_alcohol_ppm = models.FloatField()
    maximo_alcohol_ppm = models.FloatField()
    frecuencia_mediciones = models.IntegerField()
    indice_variabilidad = models.FloatField()
    
    # Metadatos
    fecha_analisis = models.DateTimeField(auto_now=True)
    numero_muestras = models.IntegerField()

    class Meta:
        ordering = ['-puntuacion_total']
        verbose_name = 'Calificación de Empleado'
        verbose_name_plural = 'Calificaciones de Empleados'

    def __str__(self):
        return f"{self.empleado.identificacion} - {self.nivel_riesgo} ({self.puntuacion_total:.2f})"

    @property
    def color_riesgo(self):
        """Retorna color para visualización según nivel de riesgo"""
        colores = {
            'BAJO': 'success',
            'MEDIO': 'warning',
            'ALTO': 'danger',
            'CRITICO': 'dark'
        }
        return colores.get(self.nivel_riesgo, 'secondary')
