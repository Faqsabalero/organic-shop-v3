from django.core.management.base import BaseCommand
from core.models import Producto

class Command(BaseCommand):
    help = 'Crea productos iniciales para pruebas'

    def handle(self, *args, **kwargs):
        productos = [
            {
                'nombre': 'Aceite de Cannabis',
                'descripcion': 'Aceite medicinal de alta calidad, elaborado con extractos puros para aliviar dolores y mejorar el bienestar.',
                'precio': 1500.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/889eeba5-5959-490d-0dde-030011bdbfb3.jpg',
            },
            {
                'nombre': 'Cápsulas de Cannabis',
                'descripcion': 'Cápsulas con dosis controlada para un tratamiento cómodo y efectivo en diversas condiciones.',
                'precio': 1200.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/1bde2c00-bbbb-40b4-4d41-22fbbb8c7193.jpg',
            },
            {
                'nombre': 'Crema Tópica',
                'descripcion': 'Crema para aplicación externa que ayuda a aliviar inflamaciones y dolores musculares.',
                'precio': 900.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/ac6727f5-e355-4ab3-e0cc-f27ad8f097e4.jpg',
            },
            {
                'nombre': 'Tintura de Cannabis',
                'descripcion': 'Extracto líquido para uso sublingual, ideal para un alivio rápido y dosificado.',
                'precio': 1300.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/2cb8c88c-bfd9-424c-5116-eb8a3a34440b.jpg',
            },
            {
                'nombre': 'Comestibles cannabis gomitas',
                'descripcion': 'Deliciosos comestibles infusionados con cannabis para un consumo discreto y placentero.',
                'precio': 1100.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/f8fa1997-06cd-4abb-4537-a116aaf5412c.jpg',
            },
            {
                'nombre': 'Vape Pen',
                'descripcion': 'Dispositivo para vapear extractos de cannabis, portátil y fácil de usar para un alivio inmediato.',
                'precio': 2500.00,
                'imagen_url': 'https://storage.googleapis.com/a1aa/image/c377d04a-aa4f-412e-9c48-7ce4748ec776.jpg',
            },
        ]

        for prod in productos:
            producto, created = Producto.objects.get_or_create(nombre=prod['nombre'], defaults=prod)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Producto '{producto.nombre}' creado."))
            else:
                self.stdout.write(f"Producto '{producto.nombre}' ya existe.")
