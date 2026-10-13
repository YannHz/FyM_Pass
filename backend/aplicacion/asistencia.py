from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import hashlib
import hmac
import secrets
import time
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .acceso import obtener_base_datos, obtener_usuario, obtener_encargado, validar_peticion
from .config import configuracion
from .models import (Persona, Usuario, Rol, Sede, Marcado, PuntoAsistencia, PuestoAbierto,
    EventoPuesto, AsignacionHorario, TramoHorario, ToleranciaRol, obtener_hora_utc)
from .seguridad import resumir_token

rutas_asistencia = APIRouter(prefix="/api", tags=["Asistencia"])


class OpcionesPunto(BaseModel):
    camara_puesto_habilitada: bool
    escaneo_movil_habilitado: bool


class LecturaQR(BaseModel):
    contenido: str = Field(min_length=1, max_length=512)
    identificador_evento: UUID


def firmar(valor: str):
    if len(configuracion.clave_qr) < 32:
        raise HTTPException(503, "Falta configurar la clave QR del servidor.")
    return hmac.new(configuracion.clave_qr.encode(), valor.encode(), hashlib.sha256).hexdigest()


def validar_firma(contenido: str, prefijo: str):
    partes = contenido.split(":")
    if len(partes) != 5 or partes[:2] != ["fym", prefijo]:
        raise HTTPException(422, "Este QR no corresponde a la modalidad elegida.")
    if not hmac.compare_digest(firmar(":".join(partes[:-1])), partes[-1]):
        raise HTTPException(422, "El QR no es válido.")
    return partes


def identidad(base: Session, persona: Persona):
    rol = base.get(Rol, persona.rol_id)
    return {"nombre": f"{persona.nombres} {persona.apellidos}", "rol": rol.nombre,
        "foto": persona.foto_ruta, "codigo": persona.codigo}


def comprobar_puesto(base: Session, puesto: PuestoAbierto):
    punto = base.get(PuntoAsistencia, puesto.punto_id)
    sede = base.get(Sede, punto.sede_id)
    encargado = base.get(Usuario, puesto.encargado_id)
    encargado_persona = base.get(Persona, encargado.persona_id)
    if not puesto.activo or puesto.vence_en <= obtener_hora_utc() or not punto.activo or not sede.activa:
        raise HTTPException(409, "El puesto está pausado o cerrado.")
    if not encargado.activo or not encargado_persona.activa or encargado.permiso not in ("administrador", "operador"):
        raise HTTPException(409, "El encargado del puesto ya no está autorizado.")
    return punto


def obtener_puesto(request: Request, base: Session = Depends(obtener_base_datos)):
    token = request.headers.get("x-fym-puesto", "")
    if not token or len(token) > 128:
        raise HTTPException(401, "Abre el puesto desde el panel del encargado.")
    puesto = base.scalar(select(PuestoAbierto).where(PuestoAbierto.token_hash == resumir_token(token)))
    if not puesto:
        raise HTTPException(401, "El acceso del puesto no es válido.")
    comprobar_puesto(base, puesto)
    return puesto


def obtener_punto_encargado(base: Session, usuario: Usuario):
    persona = base.get(Persona, usuario.persona_id)
    punto = base.scalar(select(PuntoAsistencia).where(PuntoAsistencia.sede_id == persona.sede_id).order_by(PuntoAsistencia.id))
    if not punto:
        raise HTTPException(404, "La sede no tiene punto de asistencia.")
    return punto


@rutas_asistencia.get("/asistencia/punto")
def consultar_punto(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    punto = obtener_punto_encargado(base, usuario)
    puesto = base.scalar(select(PuestoAbierto).where(PuestoAbierto.punto_id == punto.id, PuestoAbierto.activo.is_(True), PuestoAbierto.vence_en > obtener_hora_utc()))
    return {"nombre": punto.nombre, "activo": puesto is not None,
        "camara_puesto_habilitada": punto.camara_puesto_habilitada, "escaneo_movil_habilitado": punto.escaneo_movil_habilitado}


@rutas_asistencia.post("/asistencia/abrir", dependencies=[Depends(validar_peticion)])
def abrir_puesto(datos: OpcionesPunto, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    if not datos.camara_puesto_habilitada and not datos.escaneo_movil_habilitado:
        raise HTTPException(422, "Activa al menos una modalidad.")
    punto = obtener_punto_encargado(base, usuario)
    base.execute(select(PuntoAsistencia).where(PuntoAsistencia.id == punto.id).with_for_update()).scalar_one()
    punto.camara_puesto_habilitada = datos.camara_puesto_habilitada
    punto.escaneo_movil_habilitado = datos.escaneo_movil_habilitado
    base.execute(update(PuestoAbierto).where(PuestoAbierto.punto_id == punto.id).values(activo=False))
    token = secrets.token_urlsafe(32)
    puesto = PuestoAbierto(punto_id=punto.id, encargado_id=usuario.id, token_hash=resumir_token(token), activo=True, vence_en=obtener_hora_utc() + timedelta(hours=16))
    base.add(puesto)
    base.commit()
    return {"token_puesto": token}


@rutas_asistencia.post("/asistencia/pausar", dependencies=[Depends(validar_peticion)])
def pausar_puesto(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    punto = obtener_punto_encargado(base, usuario)
    base.execute(select(PuntoAsistencia).where(PuntoAsistencia.id == punto.id).with_for_update()).scalar_one()
    base.execute(update(PuestoAbierto).where(PuestoAbierto.punto_id == punto.id).values(activo=False))
    base.commit()
    return {"mensaje": "Puesto pausado. Abre nuevamente el puesto para reanudar."}


@rutas_asistencia.get("/puesto/estado")
def consultar_estado_puesto(respuesta: Response, puesto: PuestoAbierto = Depends(obtener_puesto), base: Session = Depends(obtener_base_datos)):
    punto = base.get(PuntoAsistencia, puesto.punto_id)
    bloque = int(time.time()) // 30
    valor = f"fym:puesto:{puesto.id}:{bloque}"
    respuesta.headers["Cache-Control"] = "no-store"
    return {"nombre": punto.nombre, "qr": valor + ":" + firmar(valor), "vence_en": (bloque + 1) * 30,
        "camara": punto.camara_puesto_habilitada, "movil": punto.escaneo_movil_habilitado}


@rutas_asistencia.get("/carne")
def consultar_carne(respuesta: Response, usuario: Usuario = Depends(obtener_usuario), base: Session = Depends(obtener_base_datos)):
    persona = base.get(Persona, usuario.persona_id)
    valor = f"fym:carne:{persona.id}:{persona.version_carne}"
    respuesta.headers["Cache-Control"] = "no-store"
    return {**identidad(base, persona), "sede": base.get(Sede, persona.sede_id).nombre, "qr": valor + ":" + firmar(valor)}


def formato_evento(base: Session, evento: EventoPuesto):
    persona = base.get(Persona, evento.persona_id) if evento.persona_id else None
    return {"id": evento.id, "persona": identidad(base, persona) if persona else None,
        "tipo": evento.tipo, "hora": evento.ocurrido_en.replace(tzinfo=timezone.utc).isoformat(),
        "resultado": evento.resultado, "aceptado": evento.aceptado, "repetido": False}


@rutas_asistencia.get("/puesto/eventos")
def consultar_eventos(respuesta: Response, despues: int = 0, puesto: PuestoAbierto = Depends(obtener_puesto), base: Session = Depends(obtener_base_datos)):
    eventos = base.scalars(select(EventoPuesto).where(EventoPuesto.puesto_id == puesto.id, EventoPuesto.id > despues,
        EventoPuesto.ocurrido_en > obtener_hora_utc() - timedelta(minutes=2)).order_by(EventoPuesto.id).limit(20)).all()
    respuesta.headers["Cache-Control"] = "no-store"
    return [formato_evento(base, evento) for evento in eventos]


def evaluar_entrada(base: Session, persona: Persona, ahora: datetime):
    sede = base.get(Sede, persona.sede_id)
    local = ahora.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(sede.zona_horaria))
    from .gestion import tramos_para
    tramos = tramos_para(base, persona, local.date())
    tolerancia = base.scalar(select(ToleranciaRol).where(ToleranciaRol.rol_id == persona.rol_id,
        ToleranciaRol.vigente_desde <= local.date(), (ToleranciaRol.vigente_hasta.is_(None) | (ToleranciaRol.vigente_hasta >= local.date()))).order_by(ToleranciaRol.vigente_desde.desc()))
    if not tramos or not tolerancia:
        return "Registrado · horario pendiente"
    entrada = datetime.combine(local.date(), tramos[0].hora_entrada, local.tzinfo)
    return "Puntual" if local <= entrada + timedelta(minutes=tolerancia.minutos) else "Tardanza"


def registrar_lectura(base: Session, puesto: PuestoAbierto, persona: Persona | None, datos: LecturaQR, modalidad: str, rechazo: str | None = None):
    puesto = base.scalar(select(PuestoAbierto).where(PuestoAbierto.id == puesto.id).with_for_update().execution_options(populate_existing=True))
    punto = comprobar_puesto(base, puesto)
    if (modalidad == "camara_puesto" and not punto.camara_puesto_habilitada) or (modalidad == "escaneo_movil" and not punto.escaneo_movil_habilitado):
        raise HTTPException(409, "Esta modalidad está desactivada.")
    anterior = base.scalar(select(EventoPuesto).where(EventoPuesto.identificador_evento == str(datos.identificador_evento)))
    if anterior:
        if anterior.puesto_id != puesto.id or anterior.persona_id != (persona.id if persona else None):
            raise HTTPException(409, "El identificador de lectura ya se utilizó.")
        return {**formato_evento(base, anterior), "repetido": True}
    if persona:
        persona = base.scalar(select(Persona).where(Persona.id == persona.id).with_for_update().execution_options(populate_existing=True))
    ahora = obtener_hora_utc()
    tipo = None
    rol = base.get(Rol, persona.rol_id) if persona else None
    if persona and not rechazo:
        if not persona.activa:
            rechazo = "Persona desactivada"
        elif persona.sede_id != punto.sede_id:
            rechazo = "La persona pertenece a otra sede"
    if persona and not rechazo:
        zona = ZoneInfo(base.get(Sede, persona.sede_id).zona_horaria)
        local = ahora.replace(tzinfo=timezone.utc).astimezone(zona)
        inicio = datetime.combine(local.date(), datetime.min.time(), zona).astimezone(timezone.utc).replace(tzinfo=None)
        ultimo = base.scalar(select(Marcado).where(Marcado.persona_id == persona.id, Marcado.ocurrido_en >= inicio, Marcado.ocurrido_en < inicio + timedelta(days=1)).order_by(Marcado.ocurrido_en.desc(), Marcado.id.desc()))
        if ultimo and (ahora - ultimo.ocurrido_en).total_seconds() < 10:
            evento_previo = base.scalar(select(EventoPuesto).where(EventoPuesto.marcado_id == ultimo.id))
            if evento_previo:
                return {**formato_evento(base, evento_previo), "repetido": True}
        if ultimo and (not rol.requiere_salida or ultimo.tipo == "salida"):
            rechazo = "La asistencia de hoy ya está registrada" if not rol.requiere_salida else "La entrada y salida de hoy ya están registradas"
            tipo = "entrada" if not rol.requiere_salida else "salida"
        else:
            tipo = "salida" if ultimo else "entrada"
    if persona and not rechazo and tipo == "entrada":
        from .gestion import regla_sede, tramos_para
        regla = regla_sede(base, persona.sede_id)
        tramos = tramos_para(base, persona, local.date())
        if regla.anticipacion_minutos and tramos and local < datetime.combine(local.date(), tramos[0].hora_entrada, zona) - timedelta(minutes=regla.anticipacion_minutos):
            rechazo = "El ingreso todavía no está habilitado para tu horario"
    resultado = rechazo or ("Salida registrada" if tipo == "salida" else evaluar_entrada(base, persona, ahora))
    marcado = None
    if not rechazo:
        marcado = Marcado(identificador_evento=str(datos.identificador_evento), persona_id=persona.id, punto_id=punto.id,
            rol_id=persona.rol_id, tipo=tipo, modalidad=modalidad, ocurrido_en=ahora, resultado=resultado,
            registrado_por_id=puesto.encargado_id if modalidad == "camara_puesto" else None)
        base.add(marcado)
        base.flush()
    evento = EventoPuesto(puesto_id=puesto.id, persona_id=persona.id if persona else None,
        identificador_evento=str(datos.identificador_evento), marcado_id=marcado.id if marcado else None,
        tipo=tipo, ocurrido_en=ahora, resultado=resultado, aceptado=not bool(rechazo))
    base.add(evento)
    base.commit()
    return formato_evento(base, evento)


@rutas_asistencia.post("/puesto/leer", dependencies=[Depends(validar_peticion)])
def leer_carne(datos: LecturaQR, puesto: PuestoAbierto = Depends(obtener_puesto), base: Session = Depends(obtener_base_datos)):
    persona = None
    rechazo = None
    try:
        partes = validar_firma(datos.contenido, "carne")
        persona = base.get(Persona, int(partes[2]))
        if not persona or not hmac.compare_digest(persona.version_carne, partes[3]):
            rechazo = "El carné no está vigente"
    except (HTTPException, ValueError):
        rechazo = "QR no válido. Presenta tu carné de FyM Pass"
    return registrar_lectura(base, puesto, persona, datos, "camara_puesto", rechazo)


@rutas_asistencia.post("/carne/marcar", dependencies=[Depends(validar_peticion)])
def marcar_desde_movil(datos: LecturaQR, usuario: Usuario = Depends(obtener_usuario), base: Session = Depends(obtener_base_datos)):
    partes = validar_firma(datos.contenido, "puesto")
    try:
        identificador = int(partes[2])
        bloque = int(partes[3])
    except ValueError:
        raise HTTPException(422, "El QR no es válido.")
    if bloque != int(time.time()) // 30:
        raise HTTPException(409, "El QR venció. Escanea el código actual del puesto.")
    puesto = base.get(PuestoAbierto, identificador)
    if not puesto:
        raise HTTPException(409, "El puesto no está disponible.")
    return registrar_lectura(base, puesto, base.get(Persona, usuario.persona_id), datos, "escaneo_movil")


@rutas_asistencia.get("/asistencia/marcados")
def consultar_marcados(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    persona = base.get(Persona, usuario.persona_id)
    filas = base.execute(select(Marcado, Persona, EventoPuesto.resultado).join(Persona, Marcado.persona_id == Persona.id)
        .join(PuntoAsistencia, Marcado.punto_id == PuntoAsistencia.id).outerjoin(EventoPuesto, EventoPuesto.marcado_id == Marcado.id)
        .where(PuntoAsistencia.sede_id == persona.sede_id).order_by(Marcado.id.desc()).limit(30)).all()
    return [{"id": marcado.id, "persona": identidad(base, sujeto), "tipo": marcado.tipo,
        "hora": marcado.ocurrido_en.replace(tzinfo=timezone.utc).isoformat(), "resultado": resultado or "Registrado", "modalidad": marcado.modalidad} for marcado, sujeto, resultado in filas]
