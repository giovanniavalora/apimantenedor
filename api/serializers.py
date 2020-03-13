from rest_framework import serializers
from .models import Camiones, Contratista

class ContratistaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contratista
        fields = ('id','razon_social','rut','nombre_contacto','apellido_contacto','email_contacto','telefono_contacto')

class CamionesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Camiones
        fields = ('id','patente_camion','nombre_chofer','telefono_chofer','email_chofer','id_contratista_id')
