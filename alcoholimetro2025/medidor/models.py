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