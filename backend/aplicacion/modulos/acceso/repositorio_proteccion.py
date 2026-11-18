from datetime import timedelta
import json
import secrets
import time
from cryptography.fernet import Fernet
import pyotp
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from ...models import EventoSeguridad, LimiteAcceso, Usuario, Persona, SesionAcceso, PuestoAbierto, obtener_hora_utc
from ...config import configuracion
from ...seguridad import resumir_token, verificar_clave
from ...compartido.errores import ErrorAplicacion


def cifrador():
    from pathlib import Path
    archivo = Path(__file__).resolve().parents[3] / "archivos/seguridad/clave_mfa.key"
    clave = configuracion.clave_seguridad or (archivo.read_text().strip() if archivo.exists() else "")
    if not clave:
        raise ErrorAplicacion(503, "Falta configurar la clave de protección del servidor.")
    return Fernet(clave.encode())


def registrar(base, accion, usuario=None, detalle="", sede_id=None):
    persona = base.get(Persona, usuario.persona_id) if usuario else None
    base.add(EventoSeguridad(usuario_id=usuario.id if usuario else None,
        sede_id=persona.sede_id if persona else sede_id, accion=accion, detalle=detalle[:500]))


def limitar(base, claves):
    ahora = obtener_hora_utc()
    bloqueado = False
    for prefijo, valor, maximo in claves:
        clave = resumir_token(prefijo + ":" + valor)
        sentencia = insert(LimiteAcceso).values(clave=clave, intentos=0, inicio=ahora)
        base.execute(sentencia.on_duplicate_key_update(clave=sentencia.inserted.clave))
        fila = base.scalar(select(LimiteAcceso).where(LimiteAcceso.clave == clave).with_for_update())
        if fila.bloqueado_hasta and fila.bloqueado_hasta > ahora:
            bloqueado = True
            continue
        if ahora - fila.inicio >= timedelta(minutes=15):
            fila.intentos, fila.inicio = 0, ahora
        fila.intentos += 1
        if fila.intentos > maximo:
            fila.bloqueado_hasta = ahora + timedelta(seconds=min(900, 15 * 2 ** min(fila.intentos - maximo, 6)))
            bloqueado = True
    base.commit()
    if bloqueado:
        registrar(base, "limite_acceso", None, "Espera temporal por acumulación de solicitudes.")
        base.commit()
        raise ErrorAplicacion(429, "Demasiados intentos. Espera unos minutos antes de continuar.")


def comprobar_factor(base, usuario, codigo):
    codigo = (codigo or "").strip().replace(" ", "")
    if not usuario.mfa_secreto:
        return
    secreto = cifrador().decrypt(usuario.mfa_secreto.encode()).decode()
    paso = int(time.time()) // 30
    for candidato in (paso - 1, paso, paso + 1):
        if pyotp.TOTP(secreto).at(candidato * 30) == codigo and candidato > (usuario.mfa_ultimo_paso or 0):
            usuario.mfa_ultimo_paso = candidato
            base.flush()
            return
    codigos = json.loads(usuario.mfa_recuperacion or "[]")
    resumen = resumir_token(codigo)
    if resumen in codigos:
        codigos.remove(resumen)
        usuario.mfa_recuperacion = json.dumps(codigos)
        registrar(base, "mfa_recuperacion_usada", usuario)
        base.flush()
        return
    raise ErrorAplicacion(401, "Código de verificación incorrecto o ya utilizado.")


def reautenticar(base, usuario, clave, codigo=""):
    usuario = base.scalar(select(Usuario).where(Usuario.id == usuario.id).with_for_update().execution_options(populate_existing=True))
    if not verificar_clave(clave or "", usuario.clave_hash):
        registrar(base, "reautenticacion_fallida", usuario)
        base.commit()
        raise ErrorAplicacion(401, "No se pudo verificar tu contraseña actual.")
    comprobar_factor(base, usuario, codigo)
    return usuario


def revocar(base, usuario, excepto=None):
    for sesion in base.scalars(select(SesionAcceso).where(SesionAcceso.usuario_id == usuario.id)).all():
        if sesion.token_hash != excepto:
            base.delete(sesion)
    for puesto in base.scalars(select(PuestoAbierto).where(PuestoAbierto.encargado_id == usuario.id)).all():
        puesto.activo = False


def temporal(base, usuario):
    clave = secrets.token_urlsafe(18)
    from ...seguridad import generar_hash_clave
    usuario.clave_hash = generar_hash_clave(clave)
    usuario.debe_cambiar_clave = True
    usuario.clave_temporal_vence = obtener_hora_utc() + timedelta(hours=48)
    revocar(base, usuario)
    return clave
