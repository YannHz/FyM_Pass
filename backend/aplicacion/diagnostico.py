import ipaddress
from fastapi import APIRouter, Depends, Request
from .acceso import obtener_encargado

rutas_diagnostico = APIRouter(prefix='/api/diagnostico', tags=['Diagnóstico'])


def direccion_movil(servidor):
    if not servidor:
        return None
    host, puerto = servidor
    try:
        ip = ipaddress.IPv4Address(host)
    except ipaddress.AddressValueError:
        return None
    if not ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_link_local or ip.is_multicast:
        return None
    return f'http://{ip}:{puerto}'


@rutas_diagnostico.get('/conexion')
def consultar_conexion(request: Request, usuario=Depends(obtener_encargado)):
    direccion = direccion_movil(request.scope.get('server'))
    return {'direccion_movil': direccion, 'modo': 'red' if direccion else 'local',
        'mensaje': 'Conecta el teléfono a la misma red y configura esta dirección en Flutter.' if direccion else
        'Para conectar Flutter por Wi-Fi, reinicia el sistema con --red auto o --red IP_PC.'}
