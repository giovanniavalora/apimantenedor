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

from django.core.mail import EmailMultiAlternatives
import smtplib

from django.utils import timezone
import pytz
# utc=pytz.UTC
# timezone.activate(settings.TIME_ZONE)
# timezone.localtime(timezone.now())

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse


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
        


class ProyectoViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer

class SubcontratistaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Subcontratista.objects.all()
    serializer_class = SubcontratistaSerializer

class CamionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Camion.objects.all()
    serializer_class = CamionSerializer

class CamionxProyectoList(APIView):
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
    serializer_class = DespachadorSerializer
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

    def put(self, request, pk, format=None):
        try:
            despachador = Despachador.objects.get(pk=pk)
            serializer = DespachadorSerializer(despachador, data=request.data, partial=True)
            resp={}
            if serializer.is_valid(raise_exception=True):
                serializer.save()
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


# Registra un nuevo usuario General (ni despachador ni administrador)
# class CreateUserAPIView(APIView):
#     # permission_classes = (IsAuthenticated,)
#     permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
#     def post(self, request):
#         user = request.data
#         print(user)
#         serializer = UserSerializer(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        resp = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save() #.save llamará al metodo create del serializador cuando desee crear un objeto y al método update cuando desee actualizar.
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
            serializer = DespachadorSerializer(despachador, data=request.data, partial=True)
            resp={}
            if serializer.is_valid(raise_exception=True):
                serializer.save()
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
            print("admin",admin)
            for id_proyecto in proyectos:
                admin.proyecto.add(Proyecto.objects.get(pk=id_proyecto))
            print("admin",admin)
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
            serializer = DespachadorSerializer(query, data=request.data, partial=True)
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
    



# class Texto(APIView):
#     def post(self,request):
#         # serializer_context = {
#         #     'request': request,
#         # }
#         if(request.data['proyect_id']>0):
#             adminregister=Administrador.objects.all().filter(proyecto=request.data['proyect_id'])
#             if(len(adminregister)>0):
#                 serializer = AdministradorSerializer(adminregister, many=True)
#                 return Response(serializer.data)
#             else:
#                 return Response("No existen administradores en este proyecto")
#         else:
#             return Response("Proyecto no existe")



@api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
def exportar_a_xlsx(request,start,end):

    if (not Voucher.objects.filter(fecha__range=(start,end)).exists()):
        print("\nno hay vouchers")
        res={}
        res = {'request': False, 'error': 'No existen registros para el rango especificado'}
        return Response(res,status=status.HTTP_204_NO_CONTENT)

    response = HttpResponse(
        # content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        content_type='application/vnd.ms-excel',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-reporte.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    voucher_queryset = Voucher.objects.filter(fecha__range=(start,end))
    print('voucher_queryset: ', voucher_queryset)

    camion_queryset = Voucher.objects.filter(fecha__range=(start,end)) \
        .values('patente') \
        .annotate(despachos_realizados=Count('patente')) \
        .order_by('-despachos_realizados')
    print('camion_queryset: ', camion_queryset)
    # camion_queryset = Camion.objects.all()

    workbook = Workbook()
    header_font = Font(name='Calibri', bold=True)
    # Get active worksheet/tab
    worksheet = workbook.active
    worksheet.title = 'Registro de Salida'

    print('Se ha creado la hoja de trabajo')
    # Definir los titulos por columna
    columns = [
        ('Id',5),  #1
        ('Despachador',12), #28 - falta apellido
        ('RUT Despachador',13), #29
        ('Telefono Despachador Asociado',14), #30
        ('Proyecto',10), #2
        ('Nro. impresiones',10), #3
        ('Nombre cliente',12), #no va?
        ('Rut cliente',12), #no va?
        ('Nombre subcontratista',20), #14
        ('Razón social subcontratista',20), #15
        ('RUT subcontratista',20), #16
        ('Contacto subcontratista',20), #17
        ('Email subcontratista',20), #18
        ('Teléfono subcontratista',20), #19
        ('Nombre conductor principal',20), #27
        ('Apellido conductor principal',20), #27
        ('Fecha',11), #4
        ('Hora',8), #5
        ('Patente',8), #20
        ('Marca',7), #21
        ('Modelo',8), #22
        ('Color',8), #23
        ('Volumen',8), #24
        ('Unidad de medida',8), #25
        ('Nro ejes',8), #26
        ('Foto patente',15), #32
        ('Tipo material',13), #13
        ('Punto origen',15), #6
        ('Comuna origen',16), #7
        ('Dirección origen',18), #8
        ('Punto suborigen',15), #9
        ('Punto destino',15), #10
        ('Comuna destino',16), #11
        ('Dirección destino',18), #12
    ]
    row_num = 1
    # Asignar los titulos para cada celda de la cabecera
    for col_num, (column_title, column_width) in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        # set column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = column_width
    print('Se han asignado los titulos para cada celda de la cabecera')
    # Iterar por todos los vouchers
    for voucher in voucher_queryset:
        row_num += 1
        # print("voucher.algo: ", Origen.objects.get(nombre_origen=voucher.punto_origen))
        
        # query_origen = Origen.objects.get(nombre_origen=voucher.punto_origen)
        # serializerOrigen = OrigenSerializer(query_origen)
        # print("query_origen: ", query_origen)
        # print("query_origen2: ", serializerOrigen)


        serializerOrigen=OrigenSerializer()
        if Origen.objects.filter(nombre_origen=voucher.punto_origen).exists():
            query_origen = Origen.objects.get(nombre_origen=voucher.punto_origen)
            serializerOrigen = OrigenSerializer(query_origen)
            # print('Se serializa el origen')

        serializerDestino=DestinoSerializer()
        if Destino.objects.filter(nombre_destino=voucher.punto_destino).exists():
            query_destino = Destino.objects.get(nombre_destino=voucher.punto_destino)
            serializerDestino = DestinoSerializer(query_destino)
            # print('Se serializa el destino')
        
        serializerSubcontratista=SubcontratistaSerializer()
        if Subcontratista.objects.filter(rut=voucher.rut_subcontratista).exists():
            query_subcontratista = Subcontratista.objects.get(rut=voucher.rut_subcontratista)
            serializerSubcontratista = SubcontratistaSerializer(query_subcontratista)
            # print('Se serializa el subcontratista')

        serializerCamion=CamionSerializer()
        if Camion.objects.filter(patente_camion=voucher.patente).exists():
            query_camion = Camion.objects.get(patente_camion=voucher.patente)
            serializerCamion = CamionSerializer(query_camion)
            # print('Se serializa el Camion')

        serializerDespachador=DespachadorSerializer()
        if Despachador.objects.filter(pk=voucher.despachador).exists():
            query_despachador = Despachador.objects.get(pk=voucher.despachador)
            serializerDespachador = DespachadorSerializer(query_despachador)
            # print('Se serializa el Despachador')

        
        
        # administrador = Proyecto.objects.filter(nombre_origen=despachador.proyecto, is_superuser=True)
        # Define the data for each cell in the row 
        row = [
            voucher.id, #1
            str(voucher.despachador),#28 - falta apellido
            serializerDespachador.data['rut'], #29
            serializerDespachador.data['telefono'], #30
            # voucher.proyecto,
            str(Proyecto.objects.get(id=voucher.proyecto)),#2
            voucher.contador_impresiones, #3
            voucher.nombre_cliente, #no va?
            voucher.rut_cliente, #no va?
            voucher.nombre_subcontratista, #14
            serializerSubcontratista.data['razon_social'], #15
            voucher.rut_subcontratista, #16
            serializerSubcontratista.data['nombre_contacto']+' '+serializerSubcontratista.data['apellido_contacto'], #17
            serializerSubcontratista.data['email_contacto'], #18
            serializerSubcontratista.data['telefono_contacto'], #19
            voucher.nombre_conductor_principal, #27
            voucher.apellido_conductor_principal, #27
            voucher.fecha, #4
            voucher.hora, #5
            voucher.patente, #20
            serializerCamion.data['marca_camion'], #21
            serializerCamion.data['modelo_camion'], #22
            serializerCamion.data['color_camion'], #23
            voucher.volumen, #24
            serializerCamion.data['unidad_medida'], #25
            serializerCamion.data['numero_ejes'], #26
            'https://ohl.faena.app/mediafiles/'+str(voucher.foto_patente), #32
            voucher.tipo_material, #13
            voucher.punto_origen, #6
            serializerOrigen.data['comuna'], #7
            serializerOrigen.data['calle']+' '+str(serializerOrigen.data['numero']), #8
            voucher.punto_suborigen, #9
            voucher.punto_destino, #10
            serializerDestino.data['comuna'], #11
            serializerDestino.data['calle']+' '+str(serializerDestino.data['numero']), #12
        ]
        # print('Se define la data para cada fila')
        # Asignacion de la data para cada celda de la fila
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
        # print('Se asigna la data para cada celda de la fila')


    ### Nueva hoja de trabajo ###
    # despachoscamion_queryset = Voucher.objects.filter(fecha__range=(start,end)) \
    #     .values('patente') \
    #     .annotate(despachos_realizados=Count('patente')) \
    #     .order_by('-despachos_realizados')
    # print('serializerV: ', despachoscamion_queryset)
    worksheet = workbook.create_sheet(
        title='Flota Activa',
        index=2,
    )
    print('01')
    # Definir los titulos por columna
    columns = [
        ('Subcontratista',25),
        ('Patente',10),
        ('Marca',10),
        ('Modelo',10),

        ('Color',8),
        ('Capacidad',9),
        ('Unidad',7),
        ('Numero ejes',11),

        ('Nombre conductor ppal',21),
        ('Apellido conductor ppal',21),
        
        ('Despachos realizados',19), #8
        ('Volumen total desplazado',20), #9
    ]
    print('02')
    row_num = 1
    # Asignar los titulos para cada celda de la cabecera
    for col_num, (column_title, column_width) in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        # set column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = column_width
    # Iterar por todos los camiones
    print('03')
    for camion_activo in camion_queryset:
        print('camion_activo: ',camion_activo)
        camion = Camion.objects.get(patente_camion=camion_activo['patente'])
        row_num += 1
        # Define the data for each cell in the row 
        row = [
            str(camion.subcontratista), #1
            camion.patente_camion, #2
            camion.marca_camion, #3
            camion.modelo_camion, #4

            camion.color_camion, #4
            camion.capacidad_camion, #5
            camion.unidad_medida, #6
            camion.numero_ejes, #7

            camion.nombre_conductor_principal, #?
            camion.apellido_conductor_principal, #?
            camion_activo['despachos_realizados'], #8
            int(camion_activo['despachos_realizados']) * int(camion.capacidad_camion), #9
        ]
        print('03.1')
        # Assign the data for each cell of the row 
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
        print('03.2')
    print('04')
    workbook.save(response)
    print('05')
    return response