from collections import OrderedDict
from datetime import timedelta
from threading import Lock
from time import monotonic
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import motor
from .config import configuracion
from .models import Usuario, Persona, Rol, Sede, SesionAcceso, obtener_hora_utc
from .seguridad import generar_hash_clave, verificar_clave, resumir_token

rutas = APIRouter(prefix="/api", tags=["Acceso"])
hash_ficticio = generar_hash_clave(secrets.token_urlsafe(32))
intentos = OrderedDict()
bloqueo_intentos = Lock()


class Credenciales(BaseModel):
    usuario: str = Field(min_length=1, max_length=80)
    clave: str = Field(min_length=1, max_length=256)


def obtener_base_datos():
    with Session(motor) as base:
        yield base


def validar_peticion(request: Request):
    if request.headers.get("x-fym-peticion") != "1":
        raise HTTPException(403, "Solicitud no permitida.")


def limitar_intentos(request: Request):
    direccion = request.client.host if request.client else "local"
    ahora = monotonic()
    with bloqueo_intentos:
        contador, inicio = intentos.get(direccion, (0, ahora))
        if ahora - inicio >= 60:
            contador, inicio = 0, ahora
        if contador >= 10:
            raise HTTPException(429, "Demasiados intentos. Espera un minuto y vuelve a intentar.")
        intentos[direccion] = (contador + 1, inicio)
        intentos.move_to_end(direccion)
        if len(intentos) > 10000:
            intentos.popitem(last=False)


def describir_usuario(base: Session, usuario: Usuario):
    persona = base.get(Persona, usuario.persona_id)
    rol = base.get(Rol, persona.rol_id)
    sede = base.get(Sede, persona.sede_id)
    destinos = {"administrador": "/administracion", "operador": "/operacion", "personal": "/mi-acceso"}
    return {"id": usuario.id, "usuario": usuario.nombre_usuario,
        "nombre": f"{persona.nombres} {persona.apellidos}", "rol": rol.codigo,
        "permiso": usuario.permiso, "sede": sede.nombre, "destino": destinos[usuario.permiso]}


def obtener_usuario(request: Request, base: Session = Depends(obtener_base_datos)):
    token = request.cookies.get("fym_sesion")
    if not token or len(token) > 128:
        raise HTTPException(401, "Inicia sesión para continuar.")
    sesion = base.scalar(select(SesionAcceso).where(SesionAcceso.token_hash == resumir_token(token), SesionAcceso.vence_en > obtener_hora_utc()))
    usuario = base.get(Usuario, sesion.usuario_id) if sesion else None
    persona = base.get(Persona, usuario.persona_id) if usuario else None
    sede = base.get(Sede, persona.sede_id) if persona else None
    if not usuario or not usuario.activo or not persona.activa or not sede.activa:
        raise HTTPException(401, "La sesión expiró o la cuenta no está disponible.")
    return usuario


def obtener_encargado(usuario: Usuario = Depends(obtener_usuario)):
    if usuario.permiso not in ("administrador", "operador"):
        raise HTTPException(403, "Tu cuenta no tiene acceso al panel administrativo.")
    return usuario


@rutas.post("/acceso/iniciar", dependencies=[Depends(validar_peticion), Depends(limitar_intentos)])
def iniciar_sesion(datos: Credenciales, respuesta: Response, request: Request, base: Session = Depends(obtener_base_datos)):
    usuario = base.scalar(select(Usuario).where(Usuario.nombre_usuario == datos.usuario.strip().lower()))
    correcta = verificar_clave(datos.clave, usuario.clave_hash if usuario else hash_ficticio)
    persona = base.get(Persona, usuario.persona_id) if usuario else None
    sede = base.get(Sede, persona.sede_id) if persona else None
    if not correcta or not usuario or not usuario.activo or not persona.activa or not sede.activa:
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    anterior = request.cookies.get("fym_sesion")
    if anterior:
        sesion = base.scalar(select(SesionAcceso).where(SesionAcceso.token_hash == resumir_token(anterior)))
        if sesion:
            base.delete(sesion)
    token = secrets.token_urlsafe(32)
    base.add(SesionAcceso(usuario_id=usuario.id, token_hash=resumir_token(token), vence_en=obtener_hora_utc() + timedelta(hours=8)))
    base.commit()
    respuesta.set_cookie("fym_sesion", token, httponly=True, secure=configuracion.cookie_segura, samesite="strict", max_age=28800, path="/api")
    respuesta.headers["Cache-Control"] = "no-store"
    return describir_usuario(base, usuario)


@rutas.get("/acceso/actual")
def consultar_sesion(respuesta: Response, usuario: Usuario = Depends(obtener_usuario), base: Session = Depends(obtener_base_datos)):
    respuesta.headers["Cache-Control"] = "no-store"
    return describir_usuario(base, usuario)


@rutas.post("/acceso/cerrar", dependencies=[Depends(validar_peticion)])
def cerrar_sesion(request: Request, respuesta: Response, base: Session = Depends(obtener_base_datos)):
    token = request.cookies.get("fym_sesion")
    sesion = base.scalar(select(SesionAcceso).where(SesionAcceso.token_hash == resumir_token(token))) if token else None
    if sesion:
        base.delete(sesion)
        base.commit()
    respuesta.delete_cookie("fym_sesion", path="/api", httponly=True, secure=configuracion.cookie_segura, samesite="strict")
    return {"mensaje": "Sesión cerrada."}


@rutas.get("/administracion/resumen")
def consultar_resumen(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    persona = base.get(Persona, usuario.persona_id)
    filas = base.execute(select(Rol.codigo, func.count(Persona.id)).join(Persona, Persona.rol_id == Rol.id).where(Persona.sede_id == persona.sede_id, Persona.activa.is_(True)).group_by(Rol.codigo)).all()
    return {"personas_por_rol": dict(filas), "mensaje": "Las cuentas de demostración están listas. El marcado QR se incorporará en el siguiente avance."}
