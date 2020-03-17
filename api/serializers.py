from rest_framework import serializers
from .models import Administrador, Proyecto, Despachador, Subcontratista, Camion, Origen, Suborigen, Destino, Material, Voucher


class ProyectoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proyecto
        fields = ('id','centro_de_coste','nombre_proyecto','ubicacion','cliente','rut_cliente','mandante','rut_mandante','mandante_final')

class AdministradorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administrador
        fields = ('id','username_admin','password_admin','id_proyecto_id')
        
class DespachadorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Despachador
        fields = ('id','rut_despachador','password_despachador','nombre_despachador','apellido_despachador','telefono_despachador','id_proyecto_id')

class SubcontratistaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subcontratista
        fields = ('id','rut','razon_social','nombre_subcontratista','nombre_contacto','apellido_contacto','email_contacto','telefono_contacto','id_proyecto_id')

class CamionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Camion
        fields = ('id','patente_camion','marca_camion','modelo_camion','capacidad_camion','nombre_conductor_principal','apellido_conductor_principal','telefono_conductor_principal','descripcion','QR','id_subcontratista_id')

class OrigenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Origen
        fields = ('id','nombre_origen','longitud','latitud','id_proyecto_id')

class SuborigenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Suborigen
        fields = ('id','nombre_suborigen','activo','id_origen_id')

class DestinoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Destino
        fields = ('id','nombre_destino','nombre_propietario','rut_propietario','direccion','longitud','latitud','id_proyecto_id')

class MaterialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Material
        fields = ('id','material','id_destino_id')

class VoucherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Voucher
        fields = ('id','proyecto','nombre_cliente','rut_cliente','nombre_subcontratista','rut_subcontratista',
        'nombre_conductor_principal','apellido_conductor_principal','fecha','hora','patente','volumen','tipo_material',
        'punto_origen','punto_suborigen','punto_destino','contador_impresiones','id_despachador_id')

