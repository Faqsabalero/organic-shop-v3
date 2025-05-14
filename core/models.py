from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROL_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DISTRIBUIDOR', 'Distribuidor'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='DISTRIBUIDOR')

    def __str__(self):
        return self.username

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    PLAN_PAGO_CHOICES = (
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    )
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='asignaciones_admin')
    distribuidor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='asignaciones_distribuidor')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    plan_pago = models.CharField(max_length=20, choices=PLAN_PAGO_CHOICES)

    def __str__(self):
        return f'{self.producto.nombre} - {self.distribuidor.username}'
