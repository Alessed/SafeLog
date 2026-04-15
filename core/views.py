from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import Incidente, Zona
import json
import base64
from django.http import JsonResponse
from django.core.files.base import ContentFile

class MyLoginView(LoginView):
    template_name = 'login.html'


def cerrar_sesion(request):
    request.session.flush() # Borra todos los datos de la sesión actual
    logout(request)
    response = redirect('login')
    # Forzamos al navegador a borrar cookies de sesión
    response.delete_cookie('sessionid')
    return response

@login_required
def home(request):
    context = {}
    if request.user.is_staff:
        context['notificaciones_count'] = Incidente.objects.filter(resuelto=False).count()
        context['notificaciones_recientes'] = Incidente.objects.filter(resuelto=False).order_by('-id')[:5]
    return render(request, 'home.html', context)

def splash(request):
    return render(request, 'splash.html')

@login_required
def crear_incidente(request):
    if request.method == 'POST':
        # --- DETERMINAR ORIGEN DE DATOS ---
        if request.content_type == 'application/json':
            # Datos desde el Service Worker (Offline Sync)
            data = json.loads(request.body)
            is_json = True
        else:
            # Datos desde el formulario estándar (Online)
            data = request.POST
            is_json = False

        # 1. PROCESAR GPS (Común para ambos)
        lat = data.get('latitud')
        lon = data.get('longitud')
        try:
            lat = float(lat) if lat and str(lat).strip() else None
            lon = float(lon) if lon and str(lon).strip() else None
        except ValueError:
            lat = lon = None

        # 2. LÓGICA DE ZONA QR (Común para ambos)
        zona_codigo = data.get('zona_codigo')
        descripcion_original = data.get('descripcion', '')
        
        if zona_codigo and zona_codigo != "Manual / Sin QR":
            zona_obj = Zona.objects.filter(codigo_identificador=zona_codigo).first()
            nombre_mostrar = zona_obj.nombre if zona_obj else zona_codigo
            descripcion_final = f"📍 [ZONA: {nombre_mostrar}]\n---\n{descripcion_original}"
        else:
            descripcion_final = descripcion_original

        # 3. PROCESAR IMAGEN
        if is_json:
            # Decodificar Base64 del Service Worker
            imagen_b64 = data.get('imagen')
            if imagen_b64 and ';base64,' in imagen_b64:
                format, imgstr = imagen_b64.split(';base64,')
                ext = format.split('/')[-1]
                imagen_data = ContentFile(base64.b64decode(imgstr), name=f"offline_img_{request.user.id}.{ext}")
            else:
                imagen_data = None
        else:
            # Imagen normal desde request.FILES
            imagen_data = request.FILES.get('imagen')

        # 4. GUARDAR REGISTRO
        nuevo_incidente = Incidente(
            usuario=request.user,
            titulo=data.get('titulo'),
            descripcion=descripcion_final,
            tipo=data.get('tipo'),
            imagen=imagen_data,
            latitud=lat,
            longitud=lon
        )
        nuevo_incidente.save()

        # --- RESPUESTA SEGÚN EL ORIGEN ---
        if is_json:
            return JsonResponse({'status': 'success', 'message': 'Sincronización exitosa'})
        
        return redirect('lista_incidentes')

    return render(request, 'registro_incidentes.html')

@never_cache
@login_required
def lista_incidentes(request):
    # IMPORTANTE: Pasamos las notificaciones también aquí para que la campana funcione en esta vista
    context = {}
    if request.user.is_staff:
        context['incidentes'] = Incidente.objects.all().order_by('-fecha_creacion')
        context['notificaciones_count'] = Incidente.objects.filter(resuelto=False).count()
        context['notificaciones_recientes'] = Incidente.objects.filter(resuelto=False).order_by('-id')[:5]
    else:
        context['incidentes'] = Incidente.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'historial.html', context)



@login_required
def check_notifications(request):
    if request.user.is_staff:
        # Obtenemos el ID del último incidente que el cliente ya tiene
        last_id = request.GET.get('last_id', 0)
        
        # Solo buscamos incidentes con ID mayor al que ya tiene el navegador
        nuevos_incidentes = Incidente.objects.filter(id__gt=last_id, resuelto=False).order_by('-id')
        
        count = nuevos_incidentes.count()
        
        # Preparamos los datos detallados para inyectarlos en la lista sin recargar
        data_incidentes = []
        for inc in nuevos_incidentes:
            data_incidentes.append({
                'id': inc.id,
                'titulo': inc.titulo,
                'descripcion': inc.descripcion[:100],
                'usuario': inc.usuario.username.upper(),
                'imagen_url': inc.imagen.url if inc.imagen else None,
                'fecha': inc.fecha_creacion.strftime("%H:%M")
            })
            
        return JsonResponse({
            'count': count, 
            'recientes': data_incidentes
        })
    return JsonResponse({'count': 0, 'recientes': []})