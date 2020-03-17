from django.db import models

# Create your models here.

class Proyecto(models.Model):
    centro_de_coste = models.CharField(max_length = 20, unique=True)
    nombre_proyecto = models.CharField(max_length = 100)
    ubicacion = models.CharField(max_length = 100)
    cliente = models.CharField(max_length = 100)
    rut_cliente = models.CharField(max_length = 20)
    mandante = models.CharField(max_length = 100)
    rut_mandante = models.CharField(max_length = 20)
    mandante_final = models.CharField(max_length = 100)

class Administrador(models.Model):
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    username_admin = models.CharField(max_length = 20, unique=True)
    password_admin = models.CharField(max_length=128)

class Despachador(models.Model):
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    rut_despachador = models.CharField(max_length = 20, unique=True)
    password_despachador = models.CharField(max_length=128)
    nombre_despachador = models.CharField(max_length = 50)
    apellido_despachador = models.CharField(max_length = 50)
    telefono_despachador = models.CharField(max_length = 20)

class Voucher(models.Model):
    id_despachador = models.ForeignKey(Despachador, on_delete=models.CASCADE, null=True)
    proyecto = models.CharField(max_length = 100)
    nombre_cliente = models.CharField(max_length = 50)
    rut_cliente = models.CharField(max_length = 20)
    nombre_subcontratista = models.CharField(max_length = 100)
    rut_subcontratista = models.CharField(max_length = 20)
    nombre_conductor_principal = models.CharField(max_length = 50)
    apellido_conductor_principal = models.CharField(max_length = 50)
    fecha = models.CharField(max_length = 20)
    hora = models.CharField(max_length = 20)
    patente = models.CharField(max_length = 20)
    volumen = models.CharField(max_length = 20)
    tipo_material = models.CharField(max_length = 50)
    punto_origen = models.CharField(max_length = 100)
    punto_suborigen = models.CharField(max_length = 100)
    punto_destino = models.CharField(max_length = 100)
    contador_impresiones = models.IntegerField()

class Subcontratista(models.Model):
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    rut = models.CharField(max_length = 20)
    razon_social = models.CharField(max_length = 100)
    nombre_subcontratista = models.CharField(max_length = 100)
    nombre_contacto = models.CharField(max_length = 50)
    apellido_contacto = models.CharField(max_length = 50)
    email_contacto = models.CharField(max_length = 100, blank=True, default='')
    telefono_contacto = models.CharField(max_length = 20)

class Camion(models.Model):
    id_subcontratista = models.ForeignKey(Subcontratista, on_delete=models.CASCADE, null=True)
    patente_camion = models.CharField(max_length = 20)
    marca_camion = models.CharField(max_length = 20)
    modelo_camion = models.CharField(max_length = 20)
    capacidad_camion = models.CharField(max_length = 20)
    nombre_conductor_principal = models.CharField(max_length = 50)
    apellido_conductor_principal = models.CharField(max_length = 50)
    telefono_conductor_principal = models.CharField(max_length = 20)
    descripcion = models.CharField(max_length = 20)
    QR = models.CharField(max_length = 200)    #almacenar la imagen del QR? id?

class Origen(models.Model):
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    nombre_origen = models.CharField(max_length = 100)
    longitud = models.CharField(max_length = 20)
    latitud = models.CharField(max_length = 20)

class Suborigen(models.Model):
    id_origen = models.ForeignKey(Origen, on_delete=models.CASCADE, null=True)
    nombre_suborigen = models.CharField(max_length = 20)
    activo = models.BooleanField()

class Destino(models.Model):
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True)
    nombre_destino = models.CharField(max_length = 100)
    nombre_propietario = models.CharField(max_length = 100)
    rut_propietario = models.CharField(max_length = 20)
    direccion = models.CharField(max_length = 100)
    longitud = models.CharField(max_length = 20)
    latitud = models.CharField(max_length = 20)

class Material(models.Model):
    id_destino = models.ForeignKey(Destino, on_delete=models.CASCADE, null=True)
    material = models.CharField(max_length = 50)
