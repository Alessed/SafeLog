from django.contrib import admin
from .models import Incidente, Zona

# Cambia admin.site.ModelAdmin por admin.ModelAdmin
class ZonaAdmin(admin.ModelAdmin):
    readonly_fields = ('qr_code',)

    # Esto es opcional para ver la imagen miniatura en el admin
    def qr_preview(self, obj):
        if obj.qr_code:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="150" />', obj.qr_code.url)
        return "No hay QR generado"
    
    qr_preview.short_description = 'Vista previa del QR'
    
    # Añadimos la vista previa a los campos que se muestran
    fields = ('nombre', 'codigo_identificador', 'qr_preview', 'qr_code')
    readonly_fields = ('qr_code', 'qr_preview')

# Registro de modelos
admin.site.register(Incidente)
admin.site.register(Zona, ZonaAdmin)