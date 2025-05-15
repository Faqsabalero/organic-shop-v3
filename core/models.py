from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROL_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DISTRIBUIDOR', 'Distribuidor'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='DISTRIBUIDOR')

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen_url = models.URLField()

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    PLAN_PAGO_CHOICES = (
        ('1', 'Cuota 1'),
        ('2', 'Cuota 2'),
        ('3', 'Cuota 3'),
        ('4', 'Cuota 4'),
    )
    
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
    )
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='asignaciones_admin')
    distribuidor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='asignaciones_distribuidor')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    plan_pago = models.CharField(max_length=20, choices=PLAN_PAGO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f'{self.producto.nombre} - {self.distribuidor.username}'

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    email_comprador = models.EmailField(null=True, blank=True)
    estado_pago = models.CharField(max_length=20, default='PENDIENTE')
    
    def __str__(self):
        return f'Venta {self.id} - {self.producto.nombre}'
