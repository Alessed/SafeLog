from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image


class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_identificador = models.CharField(max_length=50, unique=True)
    qr_code = models.ImageField(upload_to='qrs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Generar el QR con un borde (border) y tamaño de caja (box_size)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"safelog_zona:{self.codigo_identificador}")
        qr.make(fit=True)

        # 2. Crear la imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 3. Guardar en el buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        fname = f'qr-{self.codigo_identificador}.png'
        
        # 4. Asignar al campo ImageField
        self.qr_code.save(fname, File(buffer), save=False)
        buffer.close()
        
        super().save(*args, **kwargs)



class Incidente(models.Model):
    # Tipos de incidentes para un dropdown
    TIPOS = [
        ('MANT', 'Mantenimiento'),
        ('SEG', 'Seguridad'),
        ('LIM', 'Limpieza'),
        ('OTROS', 'Otros'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_incidentes')    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=5, choices=TIPOS, default='OTROS')
    imagen = models.ImageField(upload_to='incidentes/', null=True, blank=True)
    
    # Para el requerimiento de Elementos Físicos (GPS)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
