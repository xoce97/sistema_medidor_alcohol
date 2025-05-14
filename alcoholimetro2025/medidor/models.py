from django.db import models


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=20, unique=True)
    departamento = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"

class MuestraAlcohol(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='muestras')
    valor_analogico = models.IntegerField()
    voltaje = models.FloatField()
    alcohol_ppm = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Muestra de {self.empleado.nombre} - {self.alcohol_ppm} ppm"