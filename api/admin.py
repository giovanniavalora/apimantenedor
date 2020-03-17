from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Administrador)

admin.site.register(Proyecto)
admin.site.register(Despachador)
admin.site.register(Subcontratista)
admin.site.register(Camion)

admin.site.register(Origen)
admin.site.register(Suborigen)
admin.site.register(Destino)
admin.site.register(Material)

admin.site.register(Voucher)
