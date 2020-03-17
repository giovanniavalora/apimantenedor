#from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *


# Create your views here.
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer

class AdministradorViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.all()
    serializer_class = AdministradorSerializer
    
class DespachadorViewSet(viewsets.ModelViewSet):
    queryset = Despachador.objects.all()
    serializer_class = DespachadorSerializer

class SubcontratistaViewSet(viewsets.ModelViewSet):
    queryset = Subcontratista.objects.all()
    serializer_class = SubcontratistaSerializer

class CamionViewSet(viewsets.ModelViewSet):
    queryset = Camion.objects.all()
    serializer_class = CamionSerializer

class OrigenViewSet(viewsets.ModelViewSet):
    queryset = Origen.objects.all()
    serializer_class = OrigenSerializer

class SuborigenViewSet(viewsets.ModelViewSet):
    queryset = Suborigen.objects.all()
    serializer_class = SuborigenSerializer

class DestinoViewSet(viewsets.ModelViewSet):
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer

