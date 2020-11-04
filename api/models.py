from __future__ import unicode_literals
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)

from django.db import models

import pytz
utc=pytz.UTC
# timezone.localtime(timezone.now())


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
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.centro_de_coste



class Jornada(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    titulo_jornada = models.CharField(max_length = 100)
    hora_inicio = models.TimeField()
    duracion = models.IntegerField(default=12)
    available = models.BooleanField(default=True)    
    def __str__(self):
        return self.titulo_jornada
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['proyecto', 'titulo_jornada'], name='Jrnd_proyecto_titulojornada')
        ]


class Subcontratista(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    rut = models.CharField(max_length = 20)
    razon_social = models.CharField(max_length = 100)
    nombre_subcontratista = models.CharField(max_length = 100)
    nombre_contacto = models.CharField(max_length = 50)
    apellido_contacto = models.CharField(max_length = 50)
    email_contacto = models.CharField(max_length = 100, blank=True, default='')
    telefono_contacto = models.CharField(max_length = 20, blank=True)
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.razon_social

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['proyecto', 'rut'], name='Sbcntrtst_proyecto_rut')
        ]


def get_upload_path_camion(instance, filename):
    now = timezone.now()
    return 'fotoscamiones/{year}/{month}/{day}/subcontratista_{id_desp}/{fn}'.format(
        year=now.strftime('%Y'), month=now.strftime('%m'), day=now.strftime('%d'),
         id_desp=instance.subcontratista.id, fn=filename)

class Camion(models.Model):
    UNIDADES = [
        ('m3','m3'),
        ('ton','ton')
    ]
    # id = models.AutoField(primary_key=True)
    subcontratista = models.ForeignKey(Subcontratista, on_delete=models.CASCADE)
    patente_camion = models.CharField(max_length = 20)
    marca_camion = models.CharField(max_length = 20)
    modelo_camion = models.CharField(max_length = 20)
    capacidad_camion = models.CharField(max_length = 20)
    unidad_medida = models.CharField(max_length = 5, choices=UNIDADES)
    descripcion = models.CharField(max_length = 20, blank=True)
    numero_ejes = models.CharField(max_length = 20, blank=True)
    color_camion = models.CharField(max_length = 20, blank=True)
    foto_camion = models.FileField(upload_to=get_upload_path_camion, blank=True, null=True)
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.patente_camion+" "+self.marca_camion+" "+self.modelo_camion
    class Meta:
        verbose_name_plural = "Camiones"
        constraints = [
            models.UniqueConstraint(fields=['subcontratista', 'patente_camion'], name='Cmn_subcontratista_patente')
        ]

class Conductor(models.Model):
    subcontratista = models.ForeignKey(Subcontratista, on_delete=models.CASCADE)
    camion = models.ManyToManyField(Camion, blank=True)
    nombre = models.CharField(max_length = 30)
    apellido = models.CharField(max_length = 30)
    rut = models.CharField(max_length = 20)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length = 100, blank=True, default='')
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre+" "+self.apellido
    class Meta:
        verbose_name_plural = "Conductores"
        constraints = [
            models.UniqueConstraint(fields=['subcontratista','rut'], name='Cndctr_subcontratista_camion')
        ]


class Origen(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre_origen = models.CharField(max_length = 100)
    comuna = models.CharField(max_length = 50,blank=True)
    calle = models.CharField(max_length = 50,blank=True)
    numero = models.IntegerField(blank=True,null=True)
    latitud = models.CharField(max_length = 20)
    longitud = models.CharField(max_length = 20)
    available = models.BooleanField(default=True)
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
    comuna = models.CharField(max_length = 50,blank=True)
    calle = models.CharField(max_length = 50,blank=True)
    numero = models.IntegerField(blank=True,null=True)
    longitud = models.CharField(max_length = 20)
    latitud = models.CharField(max_length = 20)
    available = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id)+" "+self.nombre_destino


class Material(models.Model):
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    material = models.CharField(max_length = 100)
    available = models.BooleanField(default=True)
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
                # print("proceso01")
                user.save(using=self._db)
                # print("proceso02")
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
    # proyecto = models.ManyToManyField(Proyecto, related_name='proyecto', blank=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)


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
    proyecto_admin = models.ManyToManyField(Proyecto, related_name='proyecto_admin', blank=True)
    
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
    # rut_despachador = User.rut
    telefono = models.CharField(max_length=30, blank=True)
    origen_asignado = models.IntegerField(blank=True, null=True)
    proyecto_desp = models.ManyToManyField(Proyecto, related_name='proyecto_desp', blank=True)

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
        # constraints = [
        #     models.UniqueConstraint(fields=['proyecto', 'rut'], name='Dspchdr_proyecto_rut')
        # ]
##### fin usuarios #####



# # class Despachador(models.Model):
# #     rut = models.CharField(max_length=15, unique=true) 
# #     nombre = models.CharField(max_length=30)
# #     apellido = models.CharField(max_length=30)
# #     password = models.CharField(max_length=100)

# #     is_active = models.BooleanField(default=True)
# #     is_staff = models.BooleanField(default=False)
# #     date_joined = models.DateTimeField(default=timezone.now)

# #     telefono = models.CharField(max_length=30, blank=True)
# #     origen_asignado = models.IntegerField(blank=True, null=True)
# #     proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, blank=True)

# #     objects = DespManager()
# #     USERNAME_FIELD = 'rut'
# #     REQUIRED_FIELDS = ['nombre', 'apellido']
# #     def __str__(self):
# #         return self.rut
# #     def save(self, *args, **kwargs):
# #         super(User, self).save(*args, **kwargs)
# #         return self




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
    now = timezone.now()
    return 'fotospatentes/{year}/{month}/{day}/user_{id_desp}/{ahora}_{fn}'.format(
        year=now.strftime('%Y'), month=now.strftime('%m'), day=now.strftime('%d'),
         id_desp=instance.despachador.id, ahora=now, fn=filename)
class Voucher(models.Model):
    despachador = models.ForeignKey(Despachador, on_delete=models.CASCADE)
    jornada = models.ForeignKey(Jornada, on_delete=models.CASCADE)
    
    rut_despachador = models.CharField(max_length=15)
    nombre_despachador = models.CharField(max_length=30)
    apellido_despachador = models.CharField(max_length=30)
    telefono_despachador = models.CharField(max_length=30, blank=True)
    
    # id_proyecto = models.CharField(max_length = 255, blank=True)
    proyecto = models.CharField(max_length = 100)
    nombre_cliente = models.CharField(max_length = 100)
    rut_cliente = models.CharField(max_length = 20)

    # id_subcontratista = models.CharField(max_length = 255, blank=True)
    rut_subcontratista = models.CharField(max_length = 20)
    nombre_subcontratista = models.CharField(max_length = 100)
    razon_social_subcontratista = models.CharField(max_length = 100)
    nombre_contacto_subcontratista = models.CharField(max_length = 50)
    apellido_contacto_subcontratista = models.CharField(max_length = 50)
    email_contacto_subcontratista = models.CharField(max_length = 100, blank=True, default='')
    telefono_contacto_subcontratista = models.CharField(max_length = 20, blank=True)

    # id_conductor = models.CharField(max_length = 255, blank=True)
    rut_conductor = models.CharField(max_length = 20)
    nombre_conductor = models.CharField(max_length = 30)
    apellido_conductor = models.CharField(max_length = 30)

    # id_camion = models.CharField(max_length = 255, blank=True)
    patente_camion = models.CharField(max_length = 20)
    marca_camion = models.CharField(max_length = 20)
    modelo_camion = models.CharField(max_length = 20)
    capacidad_camion = models.CharField(max_length = 20)
    unidad_medida = models.CharField(max_length = 5)
    descripcion = models.CharField(max_length = 20, blank=True)
    numero_ejes = models.CharField(max_length = 20, blank=True)
    color_camion = models.CharField(max_length = 20, blank=True)
    foto_patente = models.FileField(upload_to=get_upload_path_patente)
    # foto_patente = models.FileField(upload_to='fotospatentes/%Y/%m/%d/', blank=True)

    tipo_material = models.CharField(max_length = 50)

    # id_origen = models.CharField(max_length = 255, blank=True)
    nombre_origen = models.CharField(max_length = 100)
    comuna_origen = models.CharField(max_length = 50,blank=True)
    calle_origen = models.CharField(max_length = 50,blank=True)
    numero_origen = models.IntegerField(blank=True,null=True)

    nombre_suborigen = models.CharField(max_length = 100, blank=True)

    # id_destino = models.CharField(max_length = 255, blank=True)
    nombre_destino = models.CharField(max_length = 100)
    comuna_destino = models.CharField(max_length = 50,blank=True)
    calle_destino = models.CharField(max_length = 50,blank=True)
    numero_destino = models.IntegerField(blank=True,null=True)
    
    fecha_servidor = models.DateField(auto_now_add=True)
    hora_servidor = models.TimeField(auto_now_add=True)
    fecha = models.DateField()
    hora = models.TimeField()
    contador_impresiones = models.IntegerField()
    id_qr = models.CharField(max_length = 255, blank=True) #para validar si es un qr escaneado es válido o no
    id_ticket_reemplazado = models.CharField(max_length = 255, blank=True)
    available = models.BooleanField(default=True)
    # despachos realizados (cantidad)
    # Volumen_total_desplazado_a_la_fecha

    def __str__(self):
        cadena = "voucher_"+str(self.id)+" "+str(self.despachador)
        return cadena