from django.db import models

# Create your models here.
class Contratista(models.Model):
    razon_social = models.CharField(max_length = 100)
    rut = models.CharField(max_length = 20)
    nombre_contacto = models.CharField(max_length = 50)
    apellido_contacto = models.CharField(max_length = 50)
    telefono_contacto = models.CharField(max_length=20)
    email_contacto = models.CharField(max_length = 50, blank=True, default='')
    objects = models.Manager()

    def __str__(self):
        return self.title



class Camiones(models.Model):
    id_contratista = models.ForeignKey(Contratista, on_delete=models.CASCADE)
    patente_camion = models.CharField(max_length=20)
    nombre_chofer = models.CharField(max_length=50)
    telefono_chofer = models.CharField(max_length=20)
    email_chofer = models.CharField(max_length=50, blank=True, default='')
    objects = models.Manager()

    def __str__(self):
        return self.title




class Personal_controladores_frentes(models.Model):
    nombre = models.CharField(max_length=50)
    apellido  = models.CharField(max_length=50)
    rut = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    email = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.nombre


class Proyectos(models.Model):
    nombre_proyecto = models.CharField(max_length = 50)

    def __str__(self):
        return self.nombre_proyecto


class Punto_origen(models.Model):
    id_proyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE)
    nombre_punto_origen = models.CharField(max_length = 50)
    def __str__(self):
        return self.nombre_punto_origen


class Punto_destino(models.Model):
    id_proyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE)
    nombre_punto_destino = models.CharField(max_length = 50)
    def __str__(self):
        return self.nombre_punto_destino


class Personal_controladores_frentes_proyectos(models.Model):
    id_proyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE)
    id_personal_controlador_frentes = models.ForeignKey(Personal_controladores_frentes, on_delete=models.CASCADE)


class Proyectos_contratistas(models.Model):
    id_proyecto = models.ForeignKey(Proyectos, on_delete=models.CASCADE)
    id_contratista = models.ForeignKey(Contratista, on_delete=models.CASCADE)


class Proyectos_contratistas_camiones(models.Model):
    id_camion = models.ForeignKey(Camiones, on_delete=models.CASCADE)
    id_proyecto_contratista = models.ForeignKey(Proyectos_contratistas, on_delete=models.CASCADE)
