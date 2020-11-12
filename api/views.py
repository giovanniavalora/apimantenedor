##### Auth #####
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework_jwt.utils import jwt_payload_handler

from django.conf import settings
import jwt
################

import threading

from rest_framework.parsers import MultiPartParser, FormParser #Para Subir imagen

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import *
from .models import *
from django.db.models import Count

from django.utils import timezone
import pytz
# utc=pytz.UTC
# timezone.activate(settings.TIME_ZONE)
# timezone.localtime(timezone.now())

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse





# from celery import Celery
# from celery.schedules import crontab

# app = Celery()

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_tasks(30.0, test.s('world'), expires=10)
#     sender.add_periodic_tasks(
#         crontab(hour=7, minute=30, day_of_week=1),
#         test.s('Happy Mondays!')
#     )

# @app.task
# def test(arg):
#     print(arg)

import smtplib
from django.core.mail import EmailMultiAlternatives

@api_view(['GET'])
def enviar_mail(request):
    try: 
        print("Preparando email")
        subject = '[Cambio Origen] nombre apellido '
        text_message =  "Ya está disponible tu reporte diario, visita ohl.faena.app para descargar,\n\nSaludos\nEquipo Faena"
        html_message =  '<p>Ya está disponible tu reporte diario, visita <a href="ohl.faena.app">ohl.faena.app</a> para descargar </p> \
                                                \
                        Saludos, <br>           \
                        Equipo Faena <br>           \
                        <img src="https://ohl.faena.app/avalora.png" height=20% width=20% >         \
                        '
        
        administrador = Administrador.objects.filter(is_superuser=True)
        lista_correos = []
        for admin in administrador:
            lista_correos.append(admin.email)

        message = EmailMultiAlternatives(subject,text_message,settings.EMAIL_HOST_USER,lista_correos)
        message.attach_alternative(html_message,"text/html")
        message.send()

        resp={}
        resp['message']= text_message
        return Response(resp)
    except Exception as e:
        print('error: No se pudo enviar email')
        raise e

class CodigoQRCamion(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk, format=None):
        try:
            camion = Camion.objects.get(pk=pk)
            serializer = CamionSerializer(camion)
            print(camion)

            resp={}
            resp['request']= False
            if CodigoQR.objects.filter(camion=pk).exists():
                querycodigoqr = CodigoQR.objects.filter(camion=pk)
                serializerCodigoQR = CodigoQRSerializer(querycodigoqr, many=True)
                if CodigoQR.objects.filter(camion=pk,activo=True).exists():
                    querycodigoqractivo = querycodigoqr.get(activo=True)
                    serializerCodigoQRactivo = CodigoQRSerializer(querycodigoqractivo)
                    resp['request']= True
                    resp['data']= {
                        "codigoqr_activo": serializerCodigoQRactivo.data,
                        "codigosqr": serializerCodigoQR.data,
                    }
                    return Response(resp)
                print("else?")
                resp['error']= 'El camion no posee código QR activo'
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)
            resp['error']= 'El camion no posee código QR'
            return Response(resp,status=status.HTTP_400_BAD_REQUEST)
        except Camion.DoesNotExist:
            return Response({
                'request': False,
                'error':'El subcontratista solicitado no existe'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )



class FlotaSubcontratista(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk, format=None):
        try:
            subcontratista = Subcontratista.objects.get(pk=pk)
            serializer = SubcontratistaSerializer(subcontratista)

            querycamiones = Camion.objects.filter(subcontratista=pk)
            serializerCamion = CamionSerializer(querycamiones, many=True)
            resp={}
            resp['request']= True
            resp['data']= {
                "cantidad_camiones": querycamiones.count(),
                "camiones": serializerCamion.data,
            }
            return Response(resp)
        except Subcontratista.DoesNotExist:
            return Response({
                'request': False,
                'error':'El subcontratista solicitado no existe'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CamionxProyectoList(APIView):
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    # serializer_class = DespachadorSerializer
    def get(self, request, pk, format=None):
        try:
            proyecto = Proyecto.objects.get(pk=pk)
            subcontrata = Subcontratista.objects.filter(proyecto=pk).first()
            print("subcontrata",subcontrata.proyecto)
            print(proyecto)
            print(proyecto.subcontratista_set.all())
            camiones = Camion.objects.filter(subcontratista__proyecto=pk)
            serializer = CamionSerializer(camiones, many=True)
            print(camiones)
            print(serializer.data)
            # serializer = DespachadorSerializer(despachador)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)


class ConductorxProyectoList(APIView):
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    serializer_class = ConductorSerializer
    def get(self, request, pk, format=None):
        try:
            proyecto = Proyecto.objects.get(pk=pk)
            subcontrata = Subcontratista.objects.filter(proyecto=pk).first()
            print("subcontrata",subcontrata.proyecto)
            print(proyecto)
            print(proyecto.subcontratista_set.all())
            conductores = Conductor.objects.filter(subcontratista__proyecto=pk)
            serializer = ConductorSerializer(conductores, many=True)
            print(conductores)
            print(serializer.data)
            # serializer = DespachadorSerializer(despachador)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)


#Es Similar a FlotaSubcontratista
class CamionxSubcontratistaList(APIView):
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    # serializer_class = DespachadorSerializer
    def get(self, request, pk, format=None):
        try:
            camiones = Camion.objects.filter(subcontratista=pk)
            serializer = CamionSerializer(camiones, many=True)
            print(camiones)
            print(serializer.data)
            # serializer = DespachadorSerializer(despachador)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)

class ProyectoViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    
class JornadaViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Jornada.objects.all()
    serializer_class = JornadaSerializer

class SubcontratistaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Subcontratista.objects.all()
    serializer_class = SubcontratistaSerializer

class CamionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Camion.objects.all()
    serializer_class = CamionSerializer

class ConductorViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer

class OrigenViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Origen.objects.all()
    serializer_class = OrigenSerializer

class SuborigenViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Suborigen.objects.all()
    serializer_class = SuborigenSerializer

class DestinoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class CodigoQRViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CodigoQR.objects.all()
    serializer_class = CodigoQRSerializer

class OrigenTemporalViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = OrigenTemporal.objects.all()
    serializer_class = OrigenTemporalSerializer

class VoucherViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer

class DespachadorList(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.

    def get(self, request, format=None):
        querydespachador = Despachador.objects.all()
        print(querydespachador)
        serializer = DespachadorSerializer(querydespachador, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.data
        serializer= DespachadorSerializer(data=user)

        proyectos = user['proyecto']
        del user['proyecto']

        # print("serializer.data: ", serializer.data)
        resp = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save() #.save llamará al metodo create del serializador cuando desee crear un objeto y al método update cuando desee actualizar.
            
            desp = Despachador.objects.get(rut=user['rut'])
            for id_proyecto in proyectos:
                desp.proyecto_desp.add(Proyecto.objects.get(pk=id_proyecto))#Aquí podría haber un error
            
            resp['request']= True
            resp['data']= serializer.data
            return Response(resp, status=status.HTTP_201_CREATED)
        resp['request']= False
        resp['data']= serializer.errors
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

class DespachadorDetail(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    serializer_class = DespachadorSerializer
    def get(self, request, pk, format=None):
        try:
            despachador = Despachador.objects.get(pk=pk)
            serializer = DespachadorSerializer(despachador)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            despachador = Despachador.objects.get(pk=pk)
            proyectos = request.data['proyecto']
            serializer = DespachadorSerializer(despachador, data=request.data, partial=True)
            
            resp={}
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                # despachador.proyecto_desp.all().delete()
                # for id_proyecto in proyectos:
                #     despachador.proyecto_desp.add(Proyecto.objects.get(pk=id_proyecto))
                resp['request']= True
                resp['data']= serializer.data
                return Response(resp, status=status.HTTP_200_OK)
            resp['request']= False
            resp['data']= serializer.errors
            return Response(resp, status=HTTP_400_BAD_REQUEST)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El Despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        try:
            despachador = Despachador.objects.get(pk=pk)
            despachador.delete()
            return Response({'request': True,'error':'Eliminado exitosamente'},status=status.HTTP_204_NO_CONTENT)
        except Despachador.DoesNotExist:
            return Response({'request': False,'error':'El Despachador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)


class AdministradorList(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    serializer_class = AdministradorSerializer
    def get(self, request, format=None):
        query = Administrador.objects.all()
        serializer = self.serializer_class(query, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.data
        proyectos = user['proyecto']
        del user['proyecto']
        
        serializer= self.serializer_class(data=user)
        
        resp = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save() #.save llamará al metodo create del serializador cuando desee crear un objeto y al método update cuando desee actualizar.
            admin = Administrador.objects.get(rut=user['rut'])
            
            for id_proyecto in proyectos:
                admin.proyecto_admin.add(Proyecto.objects.get(pk=id_proyecto))
            
            resp['request']= True
            resp['data']= serializer.data
            return Response(resp, status=status.HTTP_201_CREATED)
        resp['request']= False
        resp['data']= serializer.errors
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

class AdministradorDetail(APIView):
    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    serializer_class = AdministradorSerializer
    def get(self, request, pk, format=None):
        try:
            query = Administrador.objects.get(pk=pk)
            serializer = DespachadorSerializer(query)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Administrador.DoesNotExist:
            return Response({'request': False,'error':'El administrador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            query = Administrador.objects.get(pk=pk)
            serializer = AdministradorSerializer(query, data=request.data, partial=True)
            resp={}
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                resp['request']= True
                resp['data']= serializer.data
                return Response(resp, status=status.HTTP_200_OK)
            resp['request']= False
            resp['data']= serializer.errors
            return Response(resp, status=HTTP_400_BAD_REQUEST)
        except Administrador.DoesNotExist:
            return Response({'request': False,'error':'El administrador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        try:
            query = Administrador.objects.get(pk=pk)
            query.delete()
            return Response({'request': True,'error':'Eliminado exitosamente'},status=status.HTTP_204_NO_CONTENT)
        except Administrador.DoesNotExist:
            return Response({'request': False,'error':'El administrador solicitado no existe'},status=status.HTTP_400_BAD_REQUEST)

# Login (Devuelve el Token)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']
        if Administrador.objects.filter(email__iexact=email).exists():
            user = Administrador.objects.get(email__iexact=email)
            print(user)
        else:
            res = {'request': False, 'error': 'no puede autenticarse con las credenciales dadas o la cuenta ha sido desactivada'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
        if user.check_password(password):
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                serializer = AdministradorSerializer(user)
                print(serializer)
                resp = {}
                resp['request']= True
                resp['data']= {
                    'token': token,
                    'info': serializer.data
                }
                user_logged_in.send(sender=user.__class__, request=request, user=user) # almacenamos el último datetime de inicio de sesión.
                return Response(resp, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {'request': False, 'error': 'no puede autenticarse con las credenciales dadas o la cuenta ha sido desactivada'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'request': False, 'error': 'por favor proporcione un email y una password'}
        return Response(res, status=status.HTTP_403_FORBIDDEN)
    