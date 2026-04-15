from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.splash, name='splash'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('check-notifications/', views.check_notifications, name='check_notifications'),
    path('home/', views.home, name='home'),
    path('reportar/', views.crear_incidente, name='crear_incidente'),
    path('mis-reportes/', views.lista_incidentes, name='lista_incidentes'),
]