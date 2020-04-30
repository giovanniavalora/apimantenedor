from rest_framework import serializers
# from .models import User, Administrador, Despachador, Proyecto, Subcontratista, Camion, Origen, Suborigen, Destino, Material, Voucher
# from .models import Administrador, Despachador, Proyecto, Subcontratista, Camion, Origen, Suborigen, Destino, Material, Voucher
from .models import *


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'
        # fields = ('id','centro_de_coste','nombre_proyecto','ubicacion',
        # 'cliente','rut_cliente','mandante','rut_mandante','mandante_final')


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    class Meta(object):
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    def update(self, instance, validated_data):
        instance.rut = validated_data.get('rut', instance.rut)
        instance.set_password(validated_data.get('password', instance.password))
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.proyecto_id = validated_data.get('proyecto_id', instance.proyecto_id)
        instance.save()
        return instance

class AdministradorSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    class Meta(object):
        model = Administrador
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return Administrador.objects.create_superuser(**validated_data)
    def update(self, instance, validated_data):
        # instance.rut = validated_data.get('rut', instance.rut)
        instance.set_password(validated_data.get('password', instance.password))
        instance.email = validated_data.get('email', instance.email)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.proyecto_id = validated_data.get('proyecto_id', instance.proyecto_id)
        # instance.proyecto = validated_data.get('created', instance.proyecto)
        instance.save()
        return instance

class DespachadorSerializer(serializers.ModelSerializer):
    date_joined = serializers.ReadOnlyField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    class Meta(object):
        model = Despachador
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return Despachador.objects.create_user(**validated_data)
    def update(self, instance, validated_data):
        # instance.rut = validated_data.get('rut', instance.rut)
        instance.set_password(validated_data.get('password', instance.password))
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.origen_asignado = validated_data.get('origen_asignado', instance.origen_asignado)
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.apellido = validated_data.get('apellido', instance.apellido)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.proyecto_id = validated_data.get('proyecto_id', instance.proyecto_id)
        # instance.proyecto = validated_data.get('created', instance.proyecto)
        instance.save()
        return instance

class SubcontratistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcontratista
        fields = '__all__'

class CamionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camion
        fields = '__all__'

class OrigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origen
        fields = '__all__'

class SuborigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suborigen
        fields = '__all__'

class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class CodigoQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoQR
        fields = '__all__'

class OrigenTemporalSerializer(serializers.ModelSerializer):
    timestamp_inicio = serializers.ReadOnlyField()
    class Meta:
        model = OrigenTemporal
        fields = '__all__'

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = '__all__'


##### Serializers del servicio Ingresar Despacho
class IngresarDespachoSerializer(serializers.Serializer):
    vouchers = VoucherSerializer(many=True)
    # class Meta:
    #     model = Voucher
    #     fields = '__all__'



##### Serializers anidados para el servicio Sincronización Descarga
class CamionAnidadoSerializer(serializers.ModelSerializer):
    codigoqr_set = CodigoQRSerializer(many=True, read_only=True)
    class Meta:
        model = Camion
        fields = '__all__'
class SubcontratistaAnidadoSerializer(serializers.ModelSerializer):
    camion_set = CamionAnidadoSerializer(many=True, read_only=True)
    class Meta:
        model = Subcontratista
        fields = '__all__'
class DestinoAnidadoSerializer(serializers.ModelSerializer):
    material_set = MaterialSerializer(many=True, read_only=True)
    class Meta:
        model = Destino
        fields = '__all__'
class OrigenAnidadoSerializer(serializers.ModelSerializer):
    suborigen_set = SuborigenSerializer(many=True, read_only=True)
    class Meta:
        model = Origen
        fields = '__all__'

class ProyectoAnidadoSerializer(serializers.ModelSerializer):
    origen_set = OrigenAnidadoSerializer(many=True, read_only=True)
    destino_set = DestinoAnidadoSerializer(many=True, read_only=True)
    subcontratista_set = SubcontratistaAnidadoSerializer(many=True, read_only=True)
    class Meta:
        model = Proyecto
        fields = '__all__'