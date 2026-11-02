from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import motor
from ..config import configuracion
from ..models import Usuario
from ..modulos.acceso import servicios
from ..modulos.acceso.repositorio import RepositorioAcceso


def obtener_base_datos():
    with Session(motor) as base:
        yield base


def validar_peticion(request: Request):
    if request.headers.get("x-fym-peticion") != "1":
        raise HTTPException(403, "Solicitud no permitida.")


def limitar_intentos(request: Request):
    # detras de un proxy confiable la IP real llega en X-Forwarded-For
    if configuracion.proxy_confiable:
        reenviadas = request.headers.get("x-forwarded-for", "")
        cliente = reenviadas.split(",")[0].strip() or (
            request.client.host if request.client else "local"
        )
    else:
        cliente = request.client.host if request.client else "local"
    servicios.limitar_intentos(cliente)


def obtener_usuario(request: Request, base: Session = Depends(obtener_base_datos)):
    return servicios.obtener_usuario(
        request.cookies.get("fym_sesion"), RepositorioAcceso(base)
    )


def obtener_encargado(usuario: Usuario = Depends(obtener_usuario)):
    return servicios.obtener_encargado(usuario)


def administrador(usuario: Usuario = Depends(obtener_encargado)):
    from ..modulos.gestion.servicios import administrador as comprobar_administrador

    return comprobar_administrador(usuario)
