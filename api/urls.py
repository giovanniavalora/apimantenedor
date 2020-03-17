from django.urls import path, include
from rest_framework import routers
from . import views
from api.views import *

"""
app_name = "config"
"""

router = routers.DefaultRouter()
router.register(r'Administrador', views.AdministradorViewSet)
router.register(r'Proyecto', views.ProyectoViewSet)
router.register(r'Despachador', views.DespachadorViewSet)
router.register(r'Subcontratista', views.SubcontratistaViewSet)
router.register(r'Camion', views.CamionViewSet)
router.register(r'Origen', views.OrigenViewSet)
router.register(r'Suborigen', views.SuborigenViewSet)
router.register(r'Destino', views.DestinoViewSet)
router.register(r'Material', views.MaterialViewSet)
router.register(r'Voucher', views.VoucherViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
