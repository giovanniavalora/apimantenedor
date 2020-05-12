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

def export_to_xlsx(request):
    response = HttpResponse(
        # content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        content_type='application/vnd.ms-excel',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-despachos.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )
    voucher_queryset = Voucher.objects.all()
    camion_queryset = Camion.objects.all()

    workbook = Workbook()
    header_font = Font(name='Calibri', bold=True)
    # Get active worksheet/tab
    worksheet = workbook.active
    worksheet.title = 'Registro de Salida'
    # Definir los titulos por columna
    columns = [
        ('Id',5),
        ('Despachador',10),
        ('Proyecto',15),
        ('Nro. impresiones',15),
        ('Nombre cliente',15),
        ('Rut cliente',15),
        ('Nombre subcontratista',25),
        ('Nombre_conductor_principal',25),
        ('Apellido_conductor_principal',25),
        ('Fecha',10),
        ('Hora',8),
        ('Patente',8),
        ('Foto patente',15),
        ('Volumen',7),
        ('Tipo material',15),
        ('Punto origen',15),
        ('Punto suborigen',15),
        ('Punto destino',15),
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
    # Iterar por todos los vouchers
    for voucher in voucher_queryset:
        row_num += 1
        # print("voucher: ",voucher)
        # Define the data for each cell in the row 
        row = [
            voucher.id,
            str(voucher.despachador),
            voucher.proyecto,
            voucher.contador_impresiones,
            voucher.nombre_cliente,
            voucher.rut_cliente,
            voucher.nombre_subcontratista,
            voucher.nombre_conductor_principal,
            voucher.apellido_conductor_principal,
            voucher.fecha,
            voucher.hora,
            voucher.patente,
            str(voucher.foto_patente),
            voucher.volumen,
            voucher.tipo_material,
            voucher.punto_origen,
            voucher.punto_suborigen,
            voucher.punto_destino,
        ]
        # Assign the data for each cell of the row 
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value


    # Nueva hoja de trabajo
    worksheet = workbook.create_sheet(
        title='Flota Activa',
        index=2,
    )
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

        ('Nombre conductor ppal',20),
        ('Apellido conductor ppal',20),
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
    # Iterar por todos los camiones
    for camion in camion_queryset:
        row_num += 1
        # print("camion: ",camion)
        # Define the data for each cell in the row 
        row = [
            str(camion.subcontratista),
            camion.patente_camion,
            camion.marca_camion,
            camion.modelo_camion,

            camion.color_camion,
            camion.capacidad_camion,
            camion.unidad_medida,
            camion.numero_ejes,

            camion.nombre_conductor_principal,
            camion.apellido_conductor_principal,
        ]
        # Assign the data for each cell of the row 
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    workbook.save(response)
    return response



class CodigoQRCamion(APIView):
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
                print("Llegue hasta aqui")
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
        


def cambio_origen_mail(despachador,origen,id_origentemporal):
    try: 
        # Se obtiene el origen asignado oficial (si es que existe)
        origenasignado = Origen.objects.get(pk=despachador.origen_asignado)
        origentemporal = OrigenTemporal.objects.get(pk=id_origentemporal)
        inicio = origentemporal.timestamp_inicio
        duracion = timezone.timedelta(minutes=origentemporal.duracion)
        administrador = Administrador.objects.filter(proyecto=despachador.proyecto, is_superuser=True)
        
        subject = '[Cambio Origen - '+origen.nombre_origen+'] '+despachador.nombre+' '+despachador.apellido
        message = despachador.nombre+' '+despachador.apellido+'\n\n'
        message = message+'Origen asignado: '+origenasignado.nombre_origen+'\n'
        message = message+'Origen temporal: '+origen.nombre_origen+'\n\n'
        message = message+'Inicio: '+str(inicio)+'\n'
        message = message+'Fin: '+str(inicio+duracion)

        message = 'Subject: {}\n\n{}'.format(subject,message)

        server = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        # Obtener los mails de todos los admin del proyecto al que corresponde el despachador
        for admin in administrador:
            server.sendmail(settings.EMAIL_HOST_USER,admin.email,message)
            print("[Cambio de origen] correo enviado a ",admin.email)
        server.quit()
        
    except smtplib.SMTPRecipientsRefused as e:
        print('got SMTPRecipientsRefused', file=DEBUGSTREAM)
        raise e.recipients
    except Exception as e:
        raise e


class CambiarOrigenApiView(APIView):
    permission_classes = (IsAuthenticated,)
    # serializer_class = DespachadorSerializer

    def put(self, request):
        try: 
            despachador = Despachador.objects.get(pk=request.user)

            # Si ya existe un origen Temporal para el usuario se desactivará 
            if OrigenTemporal.objects.filter(despachador_id=despachador.id, activo=True).exists():
                origentemporal = OrigenTemporal.objects.get(despachador_id=despachador.id, activo=True)
                req = {'activo':False}
                serializer = OrigenTemporalSerializer(origentemporal, data=req, partial=True)
                if serializer.is_valid():
                    serializer.save()

            # Se obtiene el origen al que se quiere cambiar (si es que existe)
            origen = Origen.objects.get(pk=request.data['id_origen'])
            req = {}
            req['despachador'] = despachador.id
            req['id_origen'] = origen.id
            serializerOT = OrigenTemporalSerializer(data=req, partial=True)
            if serializerOT.is_valid(raise_exception=True):
                serializerOT.save()
                # se envía un mail a cada administrador del proyecto informando el cambio
                thread = threading.Thread(target=cambio_origen_mail, args=(despachador,origen,serializerOT.data['id']))
                thread.start()
                return Response(serializerOT.data)
            return Response(serializerOT.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e


class IngresarDespachoApiView(APIView):
    serializer_class = IngresarDespachoSerializer

    def post(self, request, *args, **kwargs):
        resp = {}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        for objeto in serializer.data["vouchers"]:
            parser_classes = (MultiPartParser, FormParser)
            file_serializer = VoucherSerializer(data=objeto)
            if file_serializer.is_valid():
                file_serializer.save()
            else:
                resp['request']= False
                resp['error'] = file_serializer.errors
                return Response(resp, status=status.HTTP_201_CREATED)
        resp['request']= True
        resp['data'] = serializer.data
        return Response(resp, status=status.HTTP_201_CREATED)

#eliminar 
class SincronizacionDescargaApiView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        despachador = Despachador.objects.get(rut=request.user)
        id_despachador = despachador.id
        id_proyecto = despachador.proyecto_id
        # origen_asignado = despachador.origen_asignado

        # serializerDespachador = DespachadorSerializer(despachador) 
        # id_despachador = serializerDespachador.data['id']
        # id_proyecto = serializerDespachador.data['proyecto']

        #Origen Asignado
        if OrigenTemporal.objects.filter(despachador_id=id_despachador, activo=True).exists():
            origentemporal = OrigenTemporal.objects.get(despachador_id=id_despachador, activo=True)
            inicio = origentemporal.timestamp_inicio
            duracion = timezone.timedelta(hours=origentemporal.duracion)
            print(inicio + duracion)
            print(timezone.now())
            if (inicio + duracion) < timezone.now():
                serializer = OrigenTemporalSerializer(origentemporal, data={'activo':False}, partial=True)
                if serializer.is_valid():
                    print("6\n",serializer,"\n")
                    serializer.save()
                # se envía el id original 
                origen_asignado = despachador.origen_asignado
            else:
                # se envía el id del OrigenTemporal activo
                origen_asignado = origentemporal.id_origen
        else:
            # se envía el id original 
            origen_asignado = despachador.origen_asignado
        

        queryproyecto = Proyecto.objects.get(id=id_proyecto)
        serializerProyecto = ProyectoAnidadoSerializer(queryproyecto)

        queryvoucher = Voucher.objects.filter(despachador=id_despachador)
        serializerVoucher = VoucherSerializer(queryvoucher, many=True)


        serializerProyecto.data['origen']= True
        descarga = {}
        descarga['request']= True
        descarga['data']= {
            "id_despachador": id_despachador,
            "id_origenAsignado": origen_asignado,
            "dataproyecto": serializerProyecto.data,
            "voucher": serializerVoucher.data
        }
        return Response(descarga, status=status.HTTP_200_OK)
        # descarga['request']= False
        # descarga['data']= serializerDespachador.errors
        # return Response(descarga, status=status.HTTP_400_BAD_REQUEST)



# class SincDesc(RetrieveUpdateAPIView):
#     serializer_class = ProyectoAnidadoSerializer
#     queryset = Proyecto.objects.all()


class ProyectoViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer

class SubcontratistaViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Subcontratista.objects.all()
    serializer_class = SubcontratistaSerializer

class CamionViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Camion.objects.all()
    serializer_class = CamionSerializer

class OrigenViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Origen.objects.all()
    serializer_class = OrigenSerializer

class SuborigenViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Suborigen.objects.all()
    serializer_class = SuborigenSerializer

class DestinoViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class CodigoQRViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = CodigoQR.objects.all()
    serializer_class = CodigoQRSerializer

class OrigenTemporalViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = OrigenTemporal.objects.all()
    serializer_class = OrigenTemporalSerializer

class VoucherViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
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
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.

    def get(self, request, format=None):
        querydespachador = Despachador.objects.all()
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
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
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
        serializer= self.serializer_class(data=user)
        resp = {}
        if serializer.is_valid(raise_exception=True):
            serializer.save() #.save llamará al metodo create del serializador cuando desee crear un objeto y al método update cuando desee actualizar.
            resp['request']= True
            resp['data']= serializer.data
            return Response(resp, status=status.HTTP_201_CREATED)
        resp['request']= False
        resp['data']= serializer.errors
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

class AdministradorDetail(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,) # permitir que cualquier usuario (autenticado o no) acceda a esta URL.
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
        if Administrador.objects.filter(email=email).exists():
            user = Administrador.objects.get(email=email)
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
