from django.urls import path, include
from rest_framework import routers
from . import views
from api.views import *

"""
app_name = "config"
"""


router = routers.DefaultRouter()
router.register(r'camiones', views.CamionesViewSet)
router.register(r'contratistas', views.ContratistasViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
