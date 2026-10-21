from ...compartido.identidad import iniciales_persona
from collections import OrderedDict
from datetime import timedelta
from threading import Lock
from time import monotonic
import secrets
from ...models import Usuario, SesionAcceso, obtener_hora_utc
from ...seguridad import generar_hash_clave, verificar_clave, resumir_token
from .repositorio import RepositorioAcceso
from ...compartido.errores import ErrorAplicacion
from .esquemas import Credenciales

hash_ficticio = generar_hash_clave(secrets.token_urlsafe(32))
intentos = OrderedDict()
bloqueo_intentos = Lock()


def limitar_intentos(direccion: str):
    ahora = monotonic()
    with bloqueo_intentos:
        contador, inicio = intentos.get(direccion, (0, ahora))
        if ahora - inicio >= 60:
            contador, inicio = (0, ahora)
        if contador >= 10:
            raise ErrorAplicacion(
                429, "Demasiados intentos. Espera un minuto y vuelve a intentar."
            )
        intentos[direccion] = (contador + 1, inicio)
        intentos.move_to_end(direccion)
        if len(intentos) > 10000:
            intentos.popitem(last=False)


def describir_usuario(repositorio: RepositorioAcceso, usuario: Usuario):
    persona = repositorio.obtener_persona(usuario.persona_id)
    rol = repositorio.obtener_rol(persona.rol_id)
    sede = repositorio.obtener_sede(persona.sede_id)
    destinos = {
        "administrador": "/administracion",
        "operador": "/operacion",
        "personal": "/mi-acceso",
    }
    return {
        "id": usuario.id,
        "usuario": usuario.nombre_usuario,
        "iniciales": iniciales_persona(persona),
        "nombre": f"{persona.nombres} {persona.apellidos}",
        "rol": rol.codigo,
        "permiso": usuario.permiso,
        "sede": sede.nombre,
        "destino": destinos[usuario.permiso],
    }


def obtener_usuario(token: str, repositorio: RepositorioAcceso):
    if not token or len(token) > 128:
        raise ErrorAplicacion(401, "Inicia sesión para continuar.")
    sesion = repositorio.sesion_vigente(obtener_hora_utc(), token)
    usuario = repositorio.obtener_usuario(sesion.usuario_id) if sesion else None
    persona = repositorio.obtener_persona(usuario.persona_id) if usuario else None
    sede = repositorio.obtener_sede(persona.sede_id) if persona else None
    if not usuario or not usuario.activo or (not persona.activa) or (not sede.activa):
        raise ErrorAplicacion(401, "La sesión expiró o la cuenta no está disponible.")
    return usuario


def obtener_encargado(usuario: Usuario = None):
    if usuario.permiso not in ("administrador", "operador"):
        raise ErrorAplicacion(403, "Tu cuenta no tiene acceso al panel administrativo.")
    return usuario


def iniciar_sesion(
    datos: Credenciales, anterior: str | None, repositorio: RepositorioAcceso = None
):
    usuario = repositorio.usuario_por_nombre(datos)
    correcta = verificar_clave(
        datos.clave, usuario.clave_hash if usuario else hash_ficticio
    )
    persona = repositorio.obtener_persona(usuario.persona_id) if usuario else None
    sede = repositorio.obtener_sede(persona.sede_id) if persona else None
    if (
        not correcta
        or not usuario
        or (not usuario.activo)
        or (not persona.activa)
        or (not sede.activa)
    ):
        raise ErrorAplicacion(401, "Usuario o contraseña incorrectos.")
    if anterior:
        sesion = repositorio.sesion_anterior(anterior)
        if sesion:
            repositorio.eliminar(sesion)
    token = secrets.token_urlsafe(32)
    repositorio.agregar(
        SesionAcceso(
            usuario_id=usuario.id,
            token_hash=resumir_token(token),
            vence_en=obtener_hora_utc() + timedelta(hours=8),
        )
    )
    repositorio.confirmar()
    return (describir_usuario(repositorio, usuario), token)


def consultar_sesion(usuario: Usuario = None, repositorio: RepositorioAcceso = None):
    return describir_usuario(repositorio, usuario)


def cerrar_sesion(token: str, repositorio: RepositorioAcceso):
    sesion = repositorio.sesion_por_token(token) if token else None
    if sesion:
        repositorio.eliminar(sesion)
        repositorio.confirmar()
    return {"mensaje": "Sesión cerrada."}


def consultar_resumen(usuario: Usuario = None, repositorio: RepositorioAcceso = None):
    persona = repositorio.obtener_persona(usuario.persona_id)
    filas = repositorio.conteos_por_rol(persona)
    return {
        "personas_por_rol": dict(filas),
        "mensaje": "Resumen de personas activas de la sede.",
    }
