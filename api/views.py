#from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CamionesSerializer, ContratistaSerializer
from .models import Camiones, Contratista


# Create your views here.
class ContratistasViewSet(viewsets.ModelViewSet):
    queryset = Contratista.objects.all()
    serializer_class = ContratistaSerializer



class CamionesViewSet(viewsets.ModelViewSet):
    queryset = Camiones.objects.all()
    serializer_class = CamionesSerializer
