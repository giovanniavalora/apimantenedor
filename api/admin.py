from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Contratista)
admin.site.register(Camiones)
admin.site.register(Personal_controladores_frentes)
admin.site.register(Proyectos)

admin.site.register(Punto_origen)
admin.site.register(Punto_destino)
admin.site.register(Personal_controladores_frentes_proyectos)
admin.site.register(Proyectos_contratistas)

admin.site.register(Proyectos_contratistas_camiones)
