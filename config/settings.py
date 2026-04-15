import os
from pathlib import Path
import dj_database_url # Necesario para procesar la URL de Postgres de Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD ---
# En Render, definiremos una variable de entorno SECRET_KEY. Si no existe, usa la de desarrollo.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-$bh-a9_8(6jv3z$13(%vpf5s6(q7a!vete_k3n=54$=@p275(d')

# DEBUG debe ser False en producción. En Render definiremos DEBUG=False.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# En producción, esto debe ser tu dominio de Render. '*' es aceptable para pruebas iniciales.
ALLOWED_HOSTS = ['*']

if not DEBUG:
    # Ajustes de seguridad para HTTPS en Render
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- ORIGENES CONFIABLES ---
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.onrender.com', # Añadimos Render
]

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # WhiteNoise arriba de staticfiles
    'django.contrib.staticfiles',
    'core',
    'pwa',
    'corsheaders'
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # Añadido para imágenes
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- BASE DE DATOS (HÍBRIDA) ---
# Si existe DATABASE_URL (en Render), la usa. Si no, usa SQLite (local).
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}

# --- ARCHIVOS ESTÁTICOS Y MEDIA ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"

# Almacenamiento eficiente para archivos estáticos en Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- OTROS AJUSTES ---
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City' # Ajustado a tu zona horaria (Coahuila)
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- PWA CONFIG ---
PWA_APP_NAME = 'SafeLog'
PWA_APP_DESCRIPTION = "Gestión de Incidentes PWA"
PWA_APP_THEME_COLOR = '#2ecc71' # Verde Neón
PWA_APP_BACKGROUND_COLOR = '#0a1f1a' # Fondo Oscuro SafeLog
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {'src': '/static/images/happy-beaming.png', 'sizes': '192x192'},
    {'src': '/static/images/happy-beaming.png', 'sizes': '512x512'}
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'