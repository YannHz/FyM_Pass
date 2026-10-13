from datetime import date, datetime, timedelta, timezone, time
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from ipaddress import ip_address
import json
from typing import Literal
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from .acceso import obtener_base_datos, obtener_encargado, validar_peticion
from .models import (Persona, Usuario, Rol, Sede, Carrera, Grupo, Horario, TramoHorario,
    AsignacionHorario, ToleranciaRol, Marcado, Justificacion, DiaNoLectivo, ReglaSede,
    TarifaDocente, Dispositivo, Auditoria, obtener_hora_utc)
from .seguridad import generar_hash_clave
from .asistencia import firmar

rutas_gestion = APIRouter(prefix='/api/gestion', tags=['Administración'])


def administrador(usuario: Usuario = Depends(obtener_encargado)):
    if usuario.permiso != 'administrador':
        raise HTTPException(403, 'Esta operación requiere permiso de administrador.')
    return usuario


def sede_usuario(base, usuario):
    return base.get(Persona, usuario.persona_id).sede_id


def comprobar_persona(base, usuario, identificador):
    persona = base.get(Persona, identificador)
    if not persona or persona.sede_id != sede_usuario(base, usuario):
        raise HTTPException(404, 'Persona no disponible en tu sede.')
    return persona


def comprobar_horario(base, sede, identificador):
    horario = base.get(Horario, identificador)
    if not horario or horario.sede_id != sede or not horario.activo:
        raise HTTPException(422, 'El horario no está disponible en esta sede.')
    return horario


def registrar_auditoria(base, usuario, accion, entidad, identificador, detalle):
    base.add(Auditoria(usuario_id=usuario.id, accion=accion, entidad=entidad, entidad_id=identificador, detalle=json.dumps(detalle, default=str, ensure_ascii=False)))


def confirmar(base):
    try:
        base.commit()
    except IntegrityError:
        base.rollback()
        raise HTTPException(409, 'Ya existe un registro con ese código, documento o usuario.')


def datos_objeto(objeto):
    return {columna.name: getattr(objeto, columna.name) for columna in objeto.__table__.columns}


def regla_sede(base, sede):
    regla = base.scalar(select(ReglaSede).where(ReglaSede.sede_id == sede))
    return regla or ReglaSede(sede_id=sede, anticipacion_minutos=0, limite_ausencia_minutos=45, observacion_porcentaje=15, alerta_porcentaje=30)


def tramos_para(base, persona, fecha):
    asignacion = base.scalar(select(AsignacionHorario).where(AsignacionHorario.persona_id == persona.id, AsignacionHorario.vigente_desde <= fecha,
        AsignacionHorario.vigente_hasta.is_(None) | (AsignacionHorario.vigente_hasta >= fecha)).order_by(AsignacionHorario.vigente_desde.desc()))
    grupo = base.get(Grupo, persona.grupo_id) if persona.grupo_id else None
    horario_id = asignacion.horario_id if asignacion else grupo.horario_id if grupo and grupo.activo else None
    horario = base.get(Horario, horario_id) if horario_id else None
    if not horario or not horario.activo:
        return []
    return base.scalars(select(TramoHorario).where(TramoHorario.horario_id == horario.id, TramoHorario.dia_semana == fecha.weekday()).order_by(TramoHorario.hora_entrada)).all()


def evaluar_manual(base, persona, instante, tipo):
    if tipo == 'salida':
        return 'Salida registrada'
    local = instante.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(base.get(Sede, persona.sede_id).zona_horaria))
    tramos = tramos_para(base, persona, local.date())
    margen = base.scalar(select(ToleranciaRol).where(ToleranciaRol.rol_id == persona.rol_id, ToleranciaRol.vigente_desde <= local.date(),
        ToleranciaRol.vigente_hasta.is_(None) | (ToleranciaRol.vigente_hasta >= local.date())).order_by(ToleranciaRol.vigente_desde.desc()))
    if not tramos or not margen:
        return 'Registrado · horario pendiente'
    limite = datetime.combine(local.date(), tramos[0].hora_entrada, local.tzinfo) + timedelta(minutes=margen.minutos)
    return 'Puntual' if local <= limite else 'Tardanza'


class Formulario(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class DatosPersona(Formulario):
    id: int | None = None
    codigo: str = Field(min_length=1, max_length=30)
    nombres: str = Field(min_length=1, max_length=100)
    apellidos: str = Field(min_length=1, max_length=100)
    documento: str | None = Field(default=None, max_length=20)
    rol_id: int
    grupo_id: int | None = None
    horario_id: int | None = None
    activa: bool = True
    identificador_biometrico: str | None = Field(default=None, max_length=40)
    tarifa_hora: Decimal = Field(default=0, ge=0, le=100000)
    nombre_usuario: str | None = Field(default=None, pattern=r'^[a-z0-9._-]{3,80}$')
    clave: str | None = Field(default=None, min_length=8, max_length=256)
    permiso: Literal['personal', 'operador', 'administrador'] = 'personal'


class DatosCarrera(Formulario):
    id: int | None = None
    nombre: str = Field(min_length=1, max_length=120)
    codigo: str = Field(min_length=1, max_length=30)
    activa: bool = True


class DatosGrupo(Formulario):
    id: int | None = None
    carrera_id: int
    horario_id: int | None = None
    codigo: str = Field(min_length=1, max_length=30)
    ciclo: str = Field(min_length=1, max_length=30)
    turno: str = Field(min_length=1, max_length=30)
    activo: bool = True


class DatosTramo(Formulario):
    dia_semana: int = Field(ge=0, le=6)
    hora_entrada: time
    hora_salida: time | None = None


class DatosHorario(Formulario):
    nombre: str = Field(min_length=1, max_length=100)
    tramos: list[DatosTramo] = Field(min_length=1, max_length=14)


class DatosManual(Formulario):
    persona_id: int
    tipo: Literal['entrada', 'salida']
    fecha_hora: datetime
    motivo: str = Field(min_length=3, max_length=500)
    identificador_evento: str = Field(min_length=36, max_length=36)


class DatosJustificacion(Formulario):
    persona_id: int
    fecha: date
    tipo: Literal['falta', 'tardanza']
    motivo: str = Field(min_length=3, max_length=1000)
    referencia: str | None = Field(default=None, max_length=200)


class ResolverJustificacion(Formulario):
    estado: Literal['aprobada', 'observada']
    observacion: str = Field(min_length=3, max_length=500)


class DatosReglas(Formulario):
    tolerancias: dict[int, int]
    anticipacion_minutos: int = Field(ge=0, le=1440)
    limite_ausencia_minutos: int = Field(ge=0, le=1440)
    observacion_porcentaje: int = Field(ge=0, le=99)
    alerta_porcentaje: int = Field(ge=1, le=100)


class DatosDia(Formulario):
    fecha: date
    motivo: str = Field(min_length=3, max_length=200)


class DatosDispositivo(Formulario):
    id: int | None = None
    nombre: str = Field(min_length=1, max_length=100)
    tipo: Literal['qr', 'zkteco']
    modelo: str | None = Field(default=None, max_length=80)
    direccion_ip: str | None = None
    puerto: int = Field(default=4370, ge=1, le=65535)
    activo: bool = True


@rutas_gestion.get('/catalogo')
def consultar_catalogo(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    sede = sede_usuario(base, usuario)
    personas = base.scalars(select(Persona).where(Persona.sede_id == sede).order_by(Persona.apellidos)).all()
    lista = []
    hoy = obtener_hora_utc().replace(tzinfo=timezone.utc).astimezone(ZoneInfo(base.get(Sede, sede).zona_horaria)).date()
    for persona in personas:
        datos = datos_objeto(persona)
        datos.pop('version_carne')
        cuenta = base.scalar(select(Usuario).where(Usuario.persona_id == persona.id))
        datos.update(nombre=f'{persona.nombres} {persona.apellidos}', rol=base.get(Rol, persona.rol_id).nombre,
            rol_codigo=base.get(Rol, persona.rol_id).codigo, nombre_usuario=cuenta.nombre_usuario if cuenta else None, permiso=cuenta.permiso if cuenta else 'personal')
        asignacion = base.scalar(select(AsignacionHorario).where(AsignacionHorario.persona_id == persona.id, AsignacionHorario.vigente_desde <= hoy,
            AsignacionHorario.vigente_hasta.is_(None) | (AsignacionHorario.vigente_hasta >= hoy)).order_by(AsignacionHorario.vigente_desde.desc()))
        datos['horario_id'] = asignacion.horario_id if asignacion else None
        tarifa = base.scalar(select(TarifaDocente).where(TarifaDocente.persona_id == persona.id))
        datos['tarifa_hora'] = float(tarifa.tarifa_hora) if tarifa and usuario.permiso == 'administrador' else 0
        lista.append(datos)
    horarios = base.scalars(select(Horario).where(Horario.sede_id == sede)).all()
    regla = regla_sede(base, sede)
    tolerancias = {}
    for rol in base.scalars(select(Rol)):
        margen = base.scalar(select(ToleranciaRol).where(ToleranciaRol.rol_id == rol.id, ToleranciaRol.vigente_desde <= hoy,
            ToleranciaRol.vigente_hasta.is_(None) | (ToleranciaRol.vigente_hasta >= hoy)).order_by(ToleranciaRol.vigente_desde.desc()))
        tolerancias[rol.id] = margen.minutos if margen else 0
    carreras = base.scalars(select(Carrera).where(Carrera.sede_id == sede)).all()
    grupos = base.scalars(select(Grupo).join(Carrera).where(Carrera.sede_id == sede)).all()
    return {'personas': lista, 'roles': [datos_objeto(rol) for rol in base.scalars(select(Rol))],
        'carreras': [datos_objeto(carrera) for carrera in carreras], 'grupos': [datos_objeto(grupo) for grupo in grupos],
        'horarios': [{**datos_objeto(horario), 'tramos': [datos_objeto(tramo) for tramo in base.scalars(select(TramoHorario).where(TramoHorario.horario_id == horario.id).order_by(TramoHorario.dia_semana, TramoHorario.hora_entrada))]} for horario in horarios],
        'reglas': {**datos_objeto(regla), 'tolerancias': tolerancias},
        'dias_no_lectivos': [datos_objeto(dia) for dia in base.scalars(select(DiaNoLectivo).where(DiaNoLectivo.sede_id == sede).order_by(DiaNoLectivo.fecha))],
        'dispositivos': [datos_objeto(dispositivo) for dispositivo in base.scalars(select(Dispositivo).where(Dispositivo.sede_id == sede))]}


@rutas_gestion.post('/personas', dependencies=[Depends(validar_peticion)])
def guardar_persona(datos: DatosPersona, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    sede = sede_usuario(base, usuario)
    if datos.id == usuario.persona_id and (not datos.activa or datos.permiso != 'administrador' or datos.rol_id != base.get(Persona, usuario.persona_id).rol_id):
        raise HTTPException(422, 'No puedes desactivar ni reducir tu propio acceso administrativo.')
    if not base.get(Rol, datos.rol_id):
        raise HTTPException(422, 'Selecciona un rol válido.')
    if datos.grupo_id:
        grupo = base.get(Grupo, datos.grupo_id)
        if not grupo or base.get(Carrera, grupo.carrera_id).sede_id != sede:
            raise HTTPException(422, 'El grupo no pertenece a tu sede.')
    if datos.horario_id:
        comprobar_horario(base, sede, datos.horario_id)
    persona = comprobar_persona(base, usuario, datos.id) if datos.id else Persona(sede_id=sede)
    campos = datos.model_dump(exclude={'id', 'horario_id', 'tarifa_hora', 'nombre_usuario', 'clave', 'permiso'})
    for campo, valor in campos.items():
        setattr(persona, campo, valor.strip() or None if isinstance(valor, str) else valor)
    base.add(persona)
    try:
        base.flush()
    except IntegrityError:
        base.rollback()
        raise HTTPException(409, 'El código, documento o ID biométrico ya existe.')
    cuenta = base.scalar(select(Usuario).where(Usuario.persona_id == persona.id))
    if datos.nombre_usuario or cuenta:
        if not cuenta and not datos.clave:
            raise HTTPException(422, 'La nueva cuenta necesita una contraseña de al menos ocho caracteres.')
        if persona.id == usuario.persona_id and (not persona.activa or datos.permiso != 'administrador'):
            raise HTTPException(422, 'No puedes desactivar tu propio acceso administrativo.')
        if datos.permiso != 'personal' and base.get(Rol, datos.rol_id).codigo != 'administrativo':
            raise HTTPException(422, 'Los permisos administrativos requieren el rol administrativo.')
        cuenta = cuenta or Usuario(persona_id=persona.id)
        cuenta.nombre_usuario = datos.nombre_usuario or cuenta.nombre_usuario
        cuenta.permiso = datos.permiso
        cuenta.activo = datos.activa
        if datos.clave:
            cuenta.clave_hash = generar_hash_clave(datos.clave)
        base.add(cuenta)
    hoy = obtener_hora_utc().replace(tzinfo=timezone.utc).astimezone(ZoneInfo('America/Lima')).date()
    actuales = base.scalars(select(AsignacionHorario).where(AsignacionHorario.persona_id == persona.id, AsignacionHorario.vigente_hasta.is_(None))).all()
    if datos.horario_id != (actuales[-1].horario_id if actuales else None):
        for actual in actuales:
            if actual.vigente_desde == hoy:
                base.delete(actual)
            else:
                actual.vigente_hasta = hoy - timedelta(days=1)
        base.flush()
        if datos.horario_id:
            base.add(AsignacionHorario(persona_id=persona.id, horario_id=datos.horario_id, vigente_desde=hoy))
    if base.get(Rol, datos.rol_id).codigo == 'docente':
        tarifa = base.scalar(select(TarifaDocente).where(TarifaDocente.persona_id == persona.id)) or TarifaDocente(persona_id=persona.id)
        tarifa.tarifa_hora = datos.tarifa_hora
        base.add(tarifa)
    registrar_auditoria(base, usuario, 'guardar_persona', 'personas', persona.id, {campo: valor for campo, valor in campos.items() if campo != 'documento'})
    confirmar(base)
    return {'id': persona.id, 'mensaje': 'Persona guardada.'}


@rutas_gestion.post('/personas/{identificador}/foto', dependencies=[Depends(validar_peticion)])
async def guardar_foto(identificador: int, archivo: UploadFile = File(...), usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    persona = comprobar_persona(base, usuario, identificador)
    contenido = await archivo.read(3 * 1024 * 1024 + 1)
    if len(contenido) > 3 * 1024 * 1024:
        raise HTTPException(422, 'La foto debe ocupar menos de 3 MB.')
    try:
        foto = Image.open(BytesIO(contenido))
        if foto.width > 4096 or foto.height > 4096:
            raise ValueError()
        foto = foto.convert('RGB')
        foto.thumbnail((512, 512))
    except (UnidentifiedImageError, ValueError, OSError):
        raise HTTPException(422, 'Selecciona una imagen JPG o PNG válida de hasta 4096 píxeles.')
    carpeta = Path(__file__).resolve().parents[1] / 'archivos/fotos'
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = str(uuid4()) + '.jpg'
    foto.save(carpeta / nombre, format='JPEG', quality=85)
    persona.foto_ruta = '/api/fotos/' + nombre
    registrar_auditoria(base, usuario, 'guardar_foto', 'personas', persona.id, {'foto': nombre})
    confirmar(base)
    return {'foto': persona.foto_ruta}


@rutas_gestion.post('/carreras', dependencies=[Depends(validar_peticion)])
def guardar_carrera(datos: DatosCarrera, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    sede = sede_usuario(base, usuario)
    carrera = base.get(Carrera, datos.id) if datos.id else Carrera(sede_id=sede)
    if not carrera or carrera.sede_id != sede:
        raise HTTPException(404, 'Carrera no disponible.')
    for campo, valor in datos.model_dump(exclude={'id'}).items():
        setattr(carrera, campo, valor)
    base.add(carrera)
    try:
        base.flush()
    except IntegrityError:
        base.rollback()
        raise HTTPException(409, 'El código de carrera ya existe.')
    registrar_auditoria(base, usuario, 'guardar_carrera', 'carreras', carrera.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Carrera guardada.'}


@rutas_gestion.post('/grupos', dependencies=[Depends(validar_peticion)])
def guardar_grupo(datos: DatosGrupo, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    sede = sede_usuario(base, usuario)
    carrera = base.get(Carrera, datos.carrera_id)
    if not carrera or carrera.sede_id != sede:
        raise HTTPException(422, 'Carrera no disponible.')
    if datos.horario_id:
        comprobar_horario(base, sede, datos.horario_id)
    grupo = base.get(Grupo, datos.id) if datos.id else Grupo()
    if not grupo or (datos.id and base.get(Carrera, grupo.carrera_id).sede_id != sede):
        raise HTTPException(404, 'Grupo no disponible.')
    for campo, valor in datos.model_dump(exclude={'id'}).items():
        setattr(grupo, campo, valor)
    base.add(grupo)
    try:
        base.flush()
    except IntegrityError:
        base.rollback()
        raise HTTPException(409, 'El código de grupo ya existe.')
    registrar_auditoria(base, usuario, 'guardar_grupo', 'grupos', grupo.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Grupo guardado.'}


@rutas_gestion.post('/horarios', dependencies=[Depends(validar_peticion)])
def guardar_horario(datos: DatosHorario, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    vistos = set()
    for tramo in datos.tramos:
        if tramo.hora_salida and tramo.hora_salida <= tramo.hora_entrada:
            raise HTTPException(422, 'La salida debe ser posterior a la entrada.')
        clave = (tramo.dia_semana, tramo.hora_entrada)
        if clave in vistos:
            raise HTTPException(422, 'Hay tramos repetidos.')
        vistos.add(clave)
    horario = Horario(nombre=datos.nombre, sede_id=sede_usuario(base, usuario))
    base.add(horario)
    base.flush()
    for tramo in datos.tramos:
        base.add(TramoHorario(horario_id=horario.id, **tramo.model_dump()))
    registrar_auditoria(base, usuario, 'crear_horario', 'horarios', horario.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Horario creado. Puedes asignarlo a personas o grupos.'}


def intervalo(base, usuario, desde, hasta):
    if hasta < desde or (hasta - desde).days > 61:
        raise HTTPException(422, 'Selecciona un intervalo de hasta 62 días.')
    sede = base.get(Sede, sede_usuario(base, usuario))
    zona = ZoneInfo(sede.zona_horaria)
    inicio = datetime.combine(desde, time.min, zona).astimezone(timezone.utc).replace(tzinfo=None)
    fin = datetime.combine(hasta + timedelta(days=1), time.min, zona).astimezone(timezone.utc).replace(tzinfo=None)
    return sede, zona, inicio, fin


def filas_diarias(base, usuario, desde, hasta):
    sede, zona, inicio, fin = intervalo(base, usuario, desde, hasta)
    personas = base.scalars(select(Persona).where(Persona.sede_id == sede.id)).all()
    marcas = base.scalars(select(Marcado).join(Persona).where(Persona.sede_id == sede.id, Marcado.ocurrido_en >= inicio, Marcado.ocurrido_en < fin).order_by(Marcado.ocurrido_en)).all()
    por_dia = {}
    for marcado in marcas:
        dia = marcado.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(zona).date()
        por_dia.setdefault((marcado.persona_id, dia), []).append(marcado)
    feriados = {dia.fecha for dia in base.scalars(select(DiaNoLectivo).where(DiaNoLectivo.sede_id == sede.id, DiaNoLectivo.fecha >= desde, DiaNoLectivo.fecha <= hasta))}
    justificaciones = {(dato.persona_id, dato.fecha): dato for dato in base.scalars(select(Justificacion).join(Persona).where(Persona.sede_id == sede.id, Justificacion.estado == 'aprobada', Justificacion.fecha >= desde, Justificacion.fecha <= hasta))}
    ahora = obtener_hora_utc().replace(tzinfo=timezone.utc).astimezone(zona)
    regla = regla_sede(base, sede.id)
    filas = []
    for numero in range((hasta - desde).days + 1):
        fecha = desde + timedelta(days=numero)
        for persona in personas:
            marcas_persona = por_dia.get((persona.id, fecha), [])
            if not persona.activa and not marcas_persona:
                continue
            rol = base.get(Rol, marcas_persona[0].rol_id if marcas_persona else persona.rol_id)
            tramos = tramos_para(base, persona, fecha)
            entrada = next((marcado for marcado in marcas_persona if marcado.tipo == 'entrada'), None)
            salida = next((marcado for marcado in marcas_persona if marcado.tipo == 'salida'), None)
            estado = entrada.resultado or evaluar_manual(base, persona, entrada.ocurrido_en, 'entrada') if entrada else 'Pendiente'
            programadas = sum((datetime.combine(fecha, tramo.hora_salida) - datetime.combine(fecha, tramo.hora_entrada)).total_seconds() / 3600 for tramo in tramos if tramo.hora_salida)
            if fecha in feriados:
                programadas = 0
            minutos = 0
            if entrada and tramos:
                local = entrada.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(zona)
                minutos = max(0, int((local - datetime.combine(fecha, tramos[0].hora_entrada, zona)).total_seconds() // 60))
            if not entrada:
                if fecha in feriados or not tramos:
                    estado = 'No programado'
                elif ahora > datetime.combine(fecha, tramos[0].hora_entrada, zona) + timedelta(minutes=regla.limite_ausencia_minutos):
                    estado = 'Falta'
            justificacion = justificaciones.get((persona.id, fecha))
            if justificacion and ((justificacion.tipo == 'falta' and estado == 'Falta') or (justificacion.tipo == 'tardanza' and estado == 'Tardanza')):
                estado = 'Justificado'
            horas = max(0, (salida.ocurrido_en - entrada.ocurrido_en).total_seconds() / 3600) if entrada and salida else 0
            grupo = base.get(Grupo, persona.grupo_id) if persona.grupo_id else None
            carrera = base.get(Carrera, grupo.carrera_id) if grupo else None
            filas.append({'persona_id': persona.id, 'codigo': persona.codigo, 'nombre': f'{persona.nombres} {persona.apellidos}', 'rol': rol.nombre, 'rol_codigo': rol.codigo,
                'fecha': str(fecha), 'entrada': entrada.ocurrido_en.replace(tzinfo=timezone.utc).isoformat() if entrada else None,
                'salida': salida.ocurrido_en.replace(tzinfo=timezone.utc).isoformat() if salida else None, 'estado': estado, 'minutos_tardanza': minutos,
                'horas_programadas': round(programadas, 2), 'horas_permanencia': round(horas, 2), 'grupo': grupo.codigo if grupo else '', 'carrera': carrera.nombre if carrera else '',
                'modalidad': entrada.modalidad if entrada else '', 'requiere_salida': rol.requiere_salida})
    return filas


@rutas_gestion.get('/diario')
def consultar_diario(desde: date, hasta: date, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    return filas_diarias(base, usuario, desde, hasta)


@rutas_gestion.get('/resumen')
def consultar_resumen(fecha: date, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    diario = filas_diarias(base, usuario, fecha, fecha)
    semana = filas_diarias(base, usuario, fecha - timedelta(days=6), fecha)
    pendientes = base.scalars(select(Justificacion).join(Persona).where(Persona.sede_id == sede_usuario(base, usuario), Justificacion.estado == 'pendiente')).all()
    return {'presentes': sum(fila['entrada'] is not None for fila in diario), 'tardanzas': sum(fila['estado'] == 'Tardanza' for fila in diario),
        'faltas': sum(fila['estado'] == 'Falta' for fila in diario), 'pendientes': len(pendientes), 'diario': diario,
        'semana': [{'fecha': str(fecha - timedelta(days=6-numero)), 'presentes': sum(fila['entrada'] is not None and fila['fecha'] == str(fecha-timedelta(days=6-numero)) for fila in semana)} for numero in range(7)]}


@rutas_gestion.post('/manual', dependencies=[Depends(validar_peticion)])
def registrar_manual(datos: DatosManual, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    persona = comprobar_persona(base, usuario, datos.persona_id)
    base.execute(select(Persona).where(Persona.id == persona.id).with_for_update()).scalar_one()
    previo = base.scalar(select(Marcado).where(Marcado.identificador_evento == datos.identificador_evento))
    if previo:
        if previo.persona_id != persona.id or previo.registrado_por_id != usuario.id:
            raise HTTPException(409, 'Ese identificador de registro ya existe.')
        return {'mensaje': 'Registro ya guardado.', 'id': previo.id}
    if not persona.activa:
        raise HTTPException(422, 'La persona está desactivada.')
    sede = base.get(Sede, persona.sede_id)
    local = datos.fecha_hora
    if local.tzinfo is None:
        local = local.replace(tzinfo=ZoneInfo(sede.zona_horaria))
    instante = local.astimezone(timezone.utc).replace(tzinfo=None)
    if instante > obtener_hora_utc() + timedelta(seconds=30):
        raise HTTPException(422, 'No puedes registrar una hora futura.')
    dia = local.astimezone(ZoneInfo(sede.zona_horaria)).date()
    _, _, inicio, fin = intervalo(base, usuario, dia, dia)
    existentes = base.scalars(select(Marcado).where(Marcado.persona_id == persona.id, Marcado.ocurrido_en >= inicio, Marcado.ocurrido_en < fin)).all()
    if any(marcado.tipo == datos.tipo for marcado in existentes):
        raise HTTPException(409, 'Ese movimiento ya está registrado para ese día.')
    if datos.tipo == 'salida':
        if not base.get(Rol, persona.rol_id).requiere_salida:
            raise HTTPException(422, 'Los estudiantes registran solamente entrada.')
        if not any(marcado.tipo == 'entrada' and marcado.ocurrido_en < instante for marcado in existentes):
            raise HTTPException(422, 'Registra primero una entrada anterior a la salida.')
    from .models import PuntoAsistencia
    punto = base.scalar(select(PuntoAsistencia).where(PuntoAsistencia.sede_id == persona.sede_id).order_by(PuntoAsistencia.id))
    resultado = evaluar_manual(base, persona, instante, datos.tipo)
    marcado = Marcado(persona_id=persona.id, punto_id=punto.id, rol_id=persona.rol_id, tipo=datos.tipo, modalidad='manual', ocurrido_en=instante,
        registrado_por_id=usuario.id, motivo=datos.motivo.strip(), identificador_evento=datos.identificador_evento, resultado=resultado)
    base.add(marcado)
    base.flush()
    registrar_auditoria(base, usuario, 'registro_manual', 'marcados', marcado.id, {'hora': instante, 'motivo': datos.motivo})
    confirmar(base)
    return {'mensaje': 'Registro manual guardado.', 'id': marcado.id}


@rutas_gestion.get('/justificaciones')
def consultar_justificaciones(usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    filas = base.execute(select(Justificacion, Persona).join(Persona).where(Persona.sede_id == sede_usuario(base, usuario)).order_by(Justificacion.id.desc())).all()
    return [{**datos_objeto(justificacion), 'nombre': f'{persona.nombres} {persona.apellidos}'} for justificacion, persona in filas]


@rutas_gestion.post('/justificaciones', dependencies=[Depends(validar_peticion)])
def crear_justificacion(datos: DatosJustificacion, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    comprobar_persona(base, usuario, datos.persona_id)
    justificacion = Justificacion(**datos.model_dump(), creada_por_id=usuario.id)
    base.add(justificacion)
    base.flush()
    registrar_auditoria(base, usuario, 'crear_justificacion', 'justificaciones', justificacion.id, {'persona_id': datos.persona_id, 'fecha': datos.fecha})
    confirmar(base)
    return {'mensaje': 'Justificación registrada.'}


@rutas_gestion.post('/justificaciones/{identificador}/resolver', dependencies=[Depends(validar_peticion)])
def resolver_justificacion(identificador: int, datos: ResolverJustificacion, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    justificacion = base.get(Justificacion, identificador)
    if not justificacion:
        raise HTTPException(404, 'Justificación no disponible.')
    comprobar_persona(base, usuario, justificacion.persona_id)
    anterior = justificacion.estado
    justificacion.estado, justificacion.observacion, justificacion.resuelta_por_id = datos.estado, datos.observacion, usuario.id
    registrar_auditoria(base, usuario, 'resolver_justificacion', 'justificaciones', justificacion.id, {'anterior': anterior, **datos.model_dump()})
    confirmar(base)
    return {'mensaje': 'Estado actualizado.'}


@rutas_gestion.post('/reglas', dependencies=[Depends(validar_peticion)])
def guardar_reglas(datos: DatosReglas, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    if datos.alerta_porcentaje <= datos.observacion_porcentaje:
        raise HTTPException(422, 'El umbral de alerta debe superar el de observación.')
    hoy = obtener_hora_utc().replace(tzinfo=timezone.utc).astimezone(ZoneInfo('America/Lima')).date()
    for identificador, minutos in datos.tolerancias.items():
        if not base.get(Rol, identificador) or not 0 <= minutos <= 1440:
            raise HTTPException(422, 'Revisa los roles y sus minutos de tolerancia.')
        margen = base.scalar(select(ToleranciaRol).where(ToleranciaRol.rol_id == identificador, ToleranciaRol.vigente_desde <= hoy, ToleranciaRol.vigente_hasta.is_(None) | (ToleranciaRol.vigente_hasta >= hoy)).order_by(ToleranciaRol.vigente_desde.desc()).with_for_update())
        if margen and margen.vigente_desde == hoy:
            margen.minutos = minutos
        else:
            if margen:
                margen.vigente_hasta = hoy - timedelta(days=1)
            base.add(ToleranciaRol(rol_id=identificador, minutos=minutos, vigente_desde=hoy))
    regla = regla_sede(base, sede_usuario(base, usuario))
    for campo, valor in datos.model_dump(exclude={'tolerancias'}).items():
        setattr(regla, campo, valor)
    base.add(regla)
    base.flush()
    registrar_auditoria(base, usuario, 'guardar_reglas', 'reglas_sedes', regla.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Reglas guardadas. Los marcados previos conservan su resultado original.'}


@rutas_gestion.post('/dias-no-lectivos', dependencies=[Depends(validar_peticion)])
def guardar_dia(datos: DatosDia, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    sede = sede_usuario(base, usuario)
    dia = base.scalar(select(DiaNoLectivo).where(DiaNoLectivo.sede_id == sede, DiaNoLectivo.fecha == datos.fecha)) or DiaNoLectivo(sede_id=sede, fecha=datos.fecha)
    dia.motivo = datos.motivo
    base.add(dia)
    base.flush()
    registrar_auditoria(base, usuario, 'guardar_dia_no_lectivo', 'dias_no_lectivos', dia.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Día no lectivo guardado.'}


@rutas_gestion.post('/dispositivos', dependencies=[Depends(validar_peticion)])
def guardar_dispositivo(datos: DatosDispositivo, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    if datos.direccion_ip:
        try:
            ip_address(datos.direccion_ip)
        except ValueError:
            raise HTTPException(422, 'Escribe una dirección IP válida.')
    sede = sede_usuario(base, usuario)
    dispositivo = base.get(Dispositivo, datos.id) if datos.id else Dispositivo(sede_id=sede)
    if not dispositivo or dispositivo.sede_id != sede:
        raise HTTPException(404, 'Dispositivo no disponible.')
    for campo, valor in datos.model_dump(exclude={'id'}).items():
        setattr(dispositivo, campo, valor)
    base.add(dispositivo)
    base.flush()
    registrar_auditoria(base, usuario, 'guardar_dispositivo', 'dispositivos', dispositivo.id, datos.model_dump())
    confirmar(base)
    return {'mensaje': 'Configuración guardada. Los biométricos no están conectados en esta demo.'}


@rutas_gestion.get('/personas/{identificador}/expediente')
def consultar_expediente(identificador: int, desde: date, hasta: date, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    persona = comprobar_persona(base, usuario, identificador)
    valor = f'fym:carne:{persona.id}:{persona.version_carne}'
    filas = [fila for fila in filas_diarias(base, usuario, desde, hasta) if fila['persona_id'] == persona.id]
    programados = [fila for fila in filas if fila['estado'] not in ('No programado', 'Pendiente')]
    faltas = sum(fila['estado'] == 'Falta' for fila in programados)
    porcentaje = round(faltas * 100 / len(programados), 1) if programados else 0
    regla = regla_sede(base, persona.sede_id)
    alerta = 'Alerta' if porcentaje >= regla.alerta_porcentaje else 'Observación' if porcentaje >= regla.observacion_porcentaje else 'Regular'
    return {'persona': {'nombre': f'{persona.nombres} {persona.apellidos}', 'codigo': persona.codigo, 'rol': base.get(Rol, persona.rol_id).nombre, 'foto': persona.foto_ruta, 'sede': base.get(Sede, persona.sede_id).nombre, 'qr': valor + ':' + firmar(valor)},
        'calendario': filas, 'faltas': faltas, 'porcentaje_faltas': porcentaje, 'alerta': alerta,
        'tramos': [datos_objeto(tramo) for tramo in tramos_para(base, persona, hasta)]}


@rutas_gestion.get('/preplanilla')
def consultar_preplanilla(desde: date, hasta: date, tarifa: Decimal | None = None, usuario: Usuario = Depends(administrador), base: Session = Depends(obtener_base_datos)):
    if tarifa is not None and not 0 <= tarifa <= 100000:
        raise HTTPException(422, 'La tarifa debe estar entre 0 y 100000.')
    filas = filas_diarias(base, usuario, desde, hasta)
    docentes = base.scalars(select(Persona).join(Rol).where(Persona.sede_id == sede_usuario(base, usuario), Rol.codigo == 'docente')).all()
    resultados = []
    for docente in docentes:
        datos = [fila for fila in filas if fila['persona_id'] == docente.id]
        configurada = base.scalar(select(TarifaDocente).where(TarifaDocente.persona_id == docente.id))
        valor = tarifa if tarifa is not None else Decimal(configurada.tarifa_hora) if configurada else Decimal(0)
        horas = sum(fila['horas_permanencia'] for fila in datos)
        minutos = sum(fila['minutos_tardanza'] for fila in datos if fila['estado'] == 'Tardanza')
        resultados.append({'persona_id': docente.id, 'nombre': f'{docente.nombres} {docente.apellidos}', 'horas_programadas': round(sum(fila['horas_programadas'] for fila in datos), 2),
            'horas_permanencia': round(horas, 2), 'minutos_tardanza': minutos, 'faltas': sum(fila['estado'] == 'Falta' for fila in datos),
            'dias_incompletos': sum(fila['entrada'] is not None and fila['salida'] is None for fila in datos), 'tarifa_hora': float(valor),
            'importe_estimado': round(float(valor) * horas, 2), 'descuento_referencial': round(float(valor) * minutos / 60, 2)})
    return resultados


@rutas_gestion.get('/exportar')
def exportar(desde: date, hasta: date, tipo: Literal['asistencia', 'preplanilla'] = 'asistencia', rol: str = '', buscar: str = '', estado: str = '', carrera: str = '', tarifa: Decimal | None = None, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    if tipo == 'preplanilla':
        if usuario.permiso != 'administrador':
            raise HTTPException(403, 'La preplanilla requiere permiso de administrador.')
        filas = consultar_preplanilla(desde, hasta, tarifa, usuario, base)
    else:
        filas = [fila for fila in filas_diarias(base, usuario, desde, hasta) if (not rol or fila['rol_codigo'] == rol) and (not estado or fila['estado'] == estado) and (not carrera or fila['carrera'] == carrera) and (not buscar or buscar.lower() in (fila['nombre'] + fila['codigo']).lower())]
    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Preplanilla estimada' if tipo == 'preplanilla' else 'Asistencia'
    columnas = list(filas[0]) if filas else ['nombre', 'fecha', 'estado']
    hoja.append([columna.replace('_', ' ').capitalize() for columna in columnas])
    for fila in filas:
        valores = []
        for columna in columnas:
            valor = fila.get(columna)
            if isinstance(valor, str) and valor.startswith(('=', '+', '-', '@', '\t', '\r')):
                valor = "'" + valor
            valores.append(valor)
        hoja.append(valores)
    for celda in hoja[1]:
        celda.font = Font(color='FFFFFF', bold=True)
        celda.fill = PatternFill('solid', fgColor='0B3C68')
    for columna in hoja.columns:
        hoja.column_dimensions[columna[0].column_letter].width = min(42, max(16, max(len(str(celda.value or '')) for celda in columna) + 2))
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    archivo = BytesIO()
    libro.save(archivo)
    archivo.seek(0)
    return StreamingResponse(archivo, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': f'attachment; filename="FyM_{tipo}_{desde}_{hasta}.xlsx"'})


@rutas_gestion.get('/marcados')
def consultar_historial_marcados(desde: date, hasta: date, usuario: Usuario = Depends(obtener_encargado), base: Session = Depends(obtener_base_datos)):
    sede, zona, inicio, fin = intervalo(base, usuario, desde, hasta)
    filas = base.execute(select(Marcado, Persona, Usuario.nombre_usuario).join(Persona, Marcado.persona_id == Persona.id).outerjoin(Usuario, Marcado.registrado_por_id == Usuario.id).where(Persona.sede_id == sede.id, Marcado.ocurrido_en >= inicio, Marcado.ocurrido_en < fin).order_by(Marcado.ocurrido_en.desc())).all()
    return [{'id': marcado.id, 'persona_id': persona.id, 'nombre': f'{persona.nombres} {persona.apellidos}', 'codigo': persona.codigo, 'tipo': marcado.tipo,
        'fecha': str(marcado.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(zona).date()), 'hora': marcado.ocurrido_en.replace(tzinfo=timezone.utc).isoformat(),
        'cargado_en': marcado.registrado_en.replace(tzinfo=timezone.utc).isoformat(), 'responsable': responsable or 'Marcado personal', 'modalidad': marcado.modalidad,
        'motivo': marcado.motivo, 'resultado': marcado.resultado or evaluar_manual(base, persona, marcado.ocurrido_en, marcado.tipo)} for marcado, persona, responsable in filas]
