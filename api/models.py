from __future__ import unicode_literals
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)

from django.db import models

import pytz
utc=pytz.UTC
timezone.localtime(timezone.now())


class Proyecto(models.Model):
    centro_de_coste = models.CharField(max_length = 20, unique=True)
    nombre_proyecto = models.CharField(max_length = 100)
    ubicacion = models.CharField(max_length = 100)
    cliente = models.CharField(max_length = 100)
    rut_cliente = models.CharField(max_length = 20)
    mandante = models.CharField(max_length = 100)
    rut_mandante = models.CharField(max_length = 20)
    mandante_final = models.CharField(max_length = 100)
    cantidad_voucher_imprimir = models.IntegerField(blank=True, default=1)

    def __str__(self):
        return self.centro_de_coste


class Subcontratista(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    rut = models.CharField(max_length = 20, unique=True)
    razon_social = models.CharField(max_length = 100)
    nombre_subcontratista = models.CharField(max_length = 100)
    nombre_contacto = models.CharField(max_length = 50)
    apellido_contacto = models.CharField(max_length = 50)
    email_contacto = models.CharField(max_length = 100, blank=True, default='')
    telefono_contacto = models.CharField(max_length = 20)
    def __str__(self):
        return self.razon_social+" "+self.rut


def get_upload_path_camion(instance, filename):
    now = datetime.now()
    return 'fotoscamiones/{year}/{month}/{day}/user_{id_desp}/{fn}'.format(
        year=now.strftime('%Y'), month=now.strftime('%m'), day=now.strftime('%d'),
         id_desp=instance.despachador.id, fn=filename)

class Camion(models.Model):
    UNIDADES = [
        ('m3','m3'),
        ('ton','ton')
    ]
    subcontratista = models.ForeignKey(Subcontratista, on_delete=models.CASCADE)
    patente_camion = models.CharField(max_length = 20, unique=True)
    marca_camion = models.CharField(max_length = 20)
    modelo_camion = models.CharField(max_length = 20)
    capacidad_camion = models.CharField(max_length = 20)
    nombre_conductor_principal = models.CharField(max_length = 50)
    apellido_conductor_principal = models.CharField(max_length = 50)
    telefono_conductor_principal = models.CharField(max_length = 20)
    descripcion = models.CharField(max_length = 20, blank=True)
    numero_ejes = models.CharField(max_length = 5)
    unidad_medida = models.CharField(max_length = 5, choices=UNIDADES)
    color_camion = models.CharField(max_length = 20)
    # foto_camion = models.FileField(upload_to=get_upload_path_camion, blank=True)
    def __str__(self):
        return self.patente_camion+" "+self.marca_camion+" "+self.modelo_camion
    class Meta:
        verbose_name_plural = "Camiones"


class Origen(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre_origen = models.CharField(max_length = 100)
    longitud = models.CharField(max_length = 20)
    latitud = models.CharField(max_length = 20)
    def __str__(self):
        return self.nombre_origen
    class Meta:
        verbose_name_plural = "Origenes"


class Suborigen(models.Model):
    origen = models.ForeignKey(Origen, on_delete=models.CASCADE)
    nombre_suborigen = models.CharField(max_length = 100)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre_suborigen+" perteneciente al origen: "+str(self.origen)
    class Meta:
        verbose_name_plural = "Sub-Origenes"


class Destino(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre_destino = models.CharField(max_length = 100)
    nombre_propietario = models.CharField(max_length = 100)
    rut_propietario = models.CharField(max_length = 20)
    direccion = models.CharField(max_length = 100)
    longitud = models.CharField(max_length = 20)
    latitud = models.CharField(max_length = 20)
    def __str__(self):
        return str(self.id)+" "+self.nombre_destino


class Material(models.Model):
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    material = models.CharField(max_length = 100)
    def __str__(self):
        return str(self.id)+" "+self.material
    class Meta:
        verbose_name_plural = "Materiales"


class CodigoQR(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id)+" "+str(self.activo)
    class Meta:
        verbose_name_plural = "Codigos QR"
    
    def save(self, *args, **kwargs):
        if not self.activo:
            return super(CodigoQR, self).save(*args, **kwargs)
        with transaction.atomic():
            CodigoQR.objects.filter(activo=True,camion=self.camion).update(activo=False)
            return super(CodigoQR, self).save(*args, **kwargs)





##### Usuarios #####
class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, rut, password, **extra_fields):
        if not rut:
            raise ValueError('The given rut must be set')
        try:
            with transaction.atomic():
                user = self.model(rut=rut, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise
    def create_user(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(rut, password, **extra_fields)    
    def create_superuser(self, rut, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(rut, password=password, **extra_fields)
        
class AdminManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, rut, password, **extra_fields):
        if not rut:
            raise ValueError('The given rut must be set')
        try:
            with transaction.atomic():
                user = self.model(rut=rut, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise
    def create_user(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(rut, password, **extra_fields)    
    def create_superuser(self, rut, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(rut, password=password, **extra_fields)

class DespManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, rut, password, **extra_fields):
        if not rut:
            raise ValueError('The given rut must be set')
        try:
            with transaction.atomic():
                user = self.model(rut=rut, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise
    def create_user(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(rut, password, **extra_fields)    
    def create_superuser(self, rut, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(rut, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=15, unique=True) 
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)

    objects = UserManager()
    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    def __str__(self):
        return self.rut
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

class Administrador(User, PermissionsMixin):
    email = models.CharField(max_length=100, unique=True)
    cargo = models.CharField(max_length=100, blank=True)
    
    objects = AdminManager()
    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    def __str__(self):
        return self.nombre
    # def save(self, *args, **kwargs):
    #     Administrador.objects.create_superuser(Administrador ,rut, password, *args, **kwargs)
    #     super(Administrador, self).save(*args, **kwargs)
    #     return self
    class Meta:
        verbose_name_plural = "Administradores"

class Despachador(User, PermissionsMixin):
    telefono = models.CharField(max_length=30, blank=True)
    origen_asignado = models.IntegerField(blank=True, null=True)

    objects = DespManager()
    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    def __str__(self):
        return self.nombre
    # def save(self, *args, **kwargs):
    #     super(Despachador, self).save(*args, **kwargs)
    #     return self
    class Meta:
        verbose_name_plural = "Despachadores"
##### fin usuarios #####





def fin_origen_temporal():
    return timezone.now() + timezone.timedelta(hours=12)
class OrigenTemporal(models.Model):
    despachador = models.ForeignKey(Despachador, on_delete=models.CASCADE)
    id_origen = models.IntegerField()
    timestamp_inicio = models.DateTimeField(default=timezone.now)
    duracion = models.IntegerField(default=12)
    activo  = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id_origen)
    class Meta:
        verbose_name_plural = "Origenes"


def get_upload_path_patente(instance, filename):
    now = datetime.now()
    return 'fotospatentes/{year}/{month}/{day}/user_{id_desp}/{fn}'.format(
        year=now.strftime('%Y'), month=now.strftime('%m'), day=now.strftime('%d'),
         id_desp=instance.despachador.id, fn=filename)
class Voucher(models.Model):
    despachador = models.ForeignKey(Despachador, on_delete=models.CASCADE)
    proyecto = models.CharField(max_length = 100)
    nombre_cliente = models.CharField(max_length = 100)
    rut_cliente = models.CharField(max_length = 20)
    nombre_subcontratista = models.CharField(max_length = 100)
    rut_subcontratista = models.CharField(max_length = 20)
    nombre_conductor_principal = models.CharField(max_length = 50)
    apellido_conductor_principal = models.CharField(max_length = 50)
    fecha_servidor = models.DateField(auto_now_add=True)
    hora_servidor = models.TimeField(auto_now_add=True)
    fecha = models.DateField()
    hora = models.TimeField()
    patente = models.CharField(max_length = 20)
    foto_patente = models.FileField(upload_to=get_upload_path_patente)
    # foto_patente = models.FileField(upload_to='fotospatentes/%Y/%m/%d/', blank=True)
    volumen = models.CharField(max_length = 20)
    tipo_material = models.CharField(max_length = 50)
    punto_origen = models.CharField(max_length = 100)
    punto_suborigen = models.CharField(max_length = 100, blank=True)
    punto_destino = models.CharField(max_length = 100)
    contador_impresiones = models.IntegerField()
    def __str__(self):
        cadena = "voucher_"+str(self.id)+" "+self.despachador
        return cadena

