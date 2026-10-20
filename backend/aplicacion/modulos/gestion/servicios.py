from ...compartido.avisos_asistencia import notificar_marcado
from ...compartido.identidad import iniciales_persona
from datetime import date, datetime, timedelta, timezone, time
from decimal import Decimal
from ipaddress import ip_address
import json
from typing import Literal
from zoneinfo import ZoneInfo
from ...models import (
    Persona,
    Usuario,
    Carrera,
    Grupo,
    Horario,
    TramoHorario,
    AsignacionHorario,
    ToleranciaRol,
    Marcado,
    Justificacion,
    DiaNoLectivo,
    ReglaSede,
    TarifaDocente,
    Dispositivo,
    Auditoria,
    obtener_hora_utc,
)
from ...seguridad import generar_hash_clave
from ...compartido.codigos_qr import firmar
from .repositorio import RepositorioGestion
from ...compartido.errores import ErrorAplicacion, ConflictoPersistencia
from ...compartido.repositorio import datos_objeto
from .esquemas import (
    DatosPersona,
    DatosCarrera,
    DatosGrupo,
    DatosHorario,
    DatosManual,
    DatosJustificacion,
    ResolverJustificacion,
    DatosReglas,
    DatosDia,
    DatosDispositivo,
)
from ...infraestructura.reportes import construir_excel


def administrador(usuario: Usuario = None):
    if usuario.permiso != "administrador":
        raise ErrorAplicacion(403, "Esta operación requiere permiso de administrador.")
    return usuario


def sede_usuario(repositorio, usuario):
    return repositorio.obtener_persona(usuario.persona_id).sede_id


def comprobar_persona(repositorio, usuario, identificador):
    persona = repositorio.obtener_persona(identificador)
    if not persona or persona.sede_id != sede_usuario(repositorio, usuario):
        raise ErrorAplicacion(404, "Persona no disponible en tu sede.")
    return persona


def comprobar_horario(repositorio, sede, identificador):
    horario = repositorio.obtener_horario(identificador)
    if not horario or horario.sede_id != sede or (not horario.activo):
        raise ErrorAplicacion(422, "El horario no está disponible en esta sede.")
    return horario


def registrar_auditoria(repositorio, usuario, accion, entidad, identificador, detalle):
    repositorio.agregar(
        Auditoria(
            usuario_id=usuario.id,
            accion=accion,
            entidad=entidad,
            entidad_id=identificador,
            detalle=json.dumps(detalle, default=str, ensure_ascii=False),
        )
    )


def confirmar(repositorio):
    try:
        repositorio.confirmar()
    except ConflictoPersistencia:
        repositorio.revertir()
        raise ErrorAplicacion(
            409, "Ya existe un registro con ese código, documento o usuario."
        )


def regla_sede(repositorio, sede):
    regla = repositorio.regla_de_sede(sede)
    return regla or ReglaSede(
        sede_id=sede,
        anticipacion_minutos=0,
        limite_ausencia_minutos=45,
        observacion_porcentaje=15,
        alerta_porcentaje=30,
    )


def tramos_para(repositorio, persona, fecha):
    asignacion = repositorio.asignacion_vigente(fecha, persona)
    grupo = repositorio.obtener_grupo(persona.grupo_id) if persona.grupo_id else None
    horario_id = (
        asignacion.horario_id
        if asignacion
        else grupo.horario_id if grupo and grupo.activo else None
    )
    horario = repositorio.obtener_horario(horario_id) if horario_id else None
    if not horario or not horario.activo:
        return []
    return repositorio.tramos_del_dia(fecha, horario)


def evaluar_manual(repositorio, persona, instante, tipo):
    if tipo == "salida":
        return "Salida registrada"
    local = instante.replace(tzinfo=timezone.utc).astimezone(
        ZoneInfo(repositorio.obtener_sede(persona.sede_id).zona_horaria)
    )
    tramos = tramos_para(repositorio, persona, local.date())
    margen = repositorio.tolerancia_vigente(local, persona)
    if not tramos or not margen:
        return "Registrado · horario pendiente"
    limite = datetime.combine(
        local.date(), tramos[0].hora_entrada, local.tzinfo
    ) + timedelta(minutes=margen.minutos)
    return "Puntual" if local <= limite else "Tardanza"


def consultar_catalogo(usuario: Usuario = None, repositorio: RepositorioGestion = None):
    sede = sede_usuario(repositorio, usuario)
    personas = repositorio.personas_ordenadas(sede)
    lista = []
    hoy = (
        obtener_hora_utc()
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo(repositorio.obtener_sede(sede).zona_horaria))
        .date()
    )
    for persona in personas:
        datos = datos_objeto(persona)
        datos.pop("version_carne")
        datos.pop("foto_ruta", None)
        cuenta = repositorio.cuenta_de_persona(persona)
        datos.update(
            nombre=f"{persona.nombres} {persona.apellidos}",
            iniciales=iniciales_persona(persona),
            rol=repositorio.obtener_rol(persona.rol_id).nombre,
            rol_codigo=repositorio.obtener_rol(persona.rol_id).codigo,
            nombre_usuario=cuenta.nombre_usuario if cuenta else None,
            permiso=cuenta.permiso if cuenta else "personal",
        )
        asignacion = repositorio.asignacion_del_catalogo(hoy, persona)
        datos["horario_id"] = asignacion.horario_id if asignacion else None
        tarifa = repositorio.tarifa_de_persona(persona)
        datos["tarifa_hora"] = (
            float(tarifa.tarifa_hora)
            if tarifa and usuario.permiso == "administrador"
            else 0
        )
        lista.append(datos)
    horarios = repositorio.horarios_de_sede(sede)
    regla = regla_sede(repositorio, sede)
    tolerancias = {}
    for rol in repositorio.roles():
        margen = repositorio.tolerancia_del_catalogo(hoy, rol)
        tolerancias[rol.id] = margen.minutos if margen else 0
    carreras = repositorio.carreras_de_sede(sede)
    grupos = repositorio.grupos_de_sede(sede)
    return {
        "personas": lista,
        "roles": [datos_objeto(rol) for rol in repositorio.roles()],
        "carreras": [datos_objeto(carrera) for carrera in carreras],
        "grupos": [datos_objeto(grupo) for grupo in grupos],
        "horarios": [
            {
                **datos_objeto(horario),
                "tramos": [
                    datos_objeto(tramo)
                    for tramo in repositorio.tramos_del_horario(horario)
                ],
            }
            for horario in horarios
        ],
        "reglas": {**datos_objeto(regla), "tolerancias": tolerancias},
        "dias_no_lectivos": [
            datos_objeto(dia) for dia in repositorio.dias_no_lectivos(sede)
        ],
        "dispositivos": [
            datos_objeto(dispositivo)
            for dispositivo in repositorio.dispositivos_de_sede(sede)
        ],
    }


def guardar_persona(
    datos: DatosPersona, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    sede = sede_usuario(repositorio, usuario)
    if datos.id == usuario.persona_id and (
        not datos.activa
        or datos.permiso != "administrador"
        or datos.rol_id != repositorio.obtener_persona(usuario.persona_id).rol_id
    ):
        raise ErrorAplicacion(
            422, "No puedes desactivar ni reducir tu propio acceso administrativo."
        )
    if not repositorio.obtener_rol(datos.rol_id):
        raise ErrorAplicacion(422, "Selecciona un rol válido.")
    if datos.grupo_id:
        grupo = repositorio.obtener_grupo(datos.grupo_id)
        if not grupo or repositorio.obtener_carrera(grupo.carrera_id).sede_id != sede:
            raise ErrorAplicacion(422, "El grupo no pertenece a tu sede.")
    if datos.horario_id:
        comprobar_horario(repositorio, sede, datos.horario_id)
    persona = (
        comprobar_persona(repositorio, usuario, datos.id)
        if datos.id
        else Persona(sede_id=sede)
    )
    campos = datos.model_dump(
        exclude={
            "id",
            "horario_id",
            "tarifa_hora",
            "nombre_usuario",
            "clave",
            "permiso",
        }
    )
    for campo, valor in campos.items():
        setattr(
            persona, campo, valor.strip() or None if isinstance(valor, str) else valor
        )
    repositorio.agregar(persona)
    try:
        repositorio.sincronizar()
    except ConflictoPersistencia:
        repositorio.revertir()
        raise ErrorAplicacion(409, "El código, documento o ID biométrico ya existe.")
    cuenta = repositorio.cuenta_de_persona(persona)
    if datos.nombre_usuario or cuenta:
        if not cuenta and (not datos.clave):
            raise ErrorAplicacion(
                422,
                "La nueva cuenta necesita una contraseña de al menos ocho caracteres.",
            )
        if persona.id == usuario.persona_id and (
            not persona.activa or datos.permiso != "administrador"
        ):
            raise ErrorAplicacion(
                422, "No puedes desactivar tu propio acceso administrativo."
            )
        if (
            datos.permiso != "personal"
            and repositorio.obtener_rol(datos.rol_id).codigo != "administrativo"
        ):
            raise ErrorAplicacion(
                422, "Los permisos administrativos requieren el rol administrativo."
            )
        cuenta = cuenta or Usuario(persona_id=persona.id)
        cuenta.nombre_usuario = datos.nombre_usuario or cuenta.nombre_usuario
        cuenta.permiso = datos.permiso
        cuenta.activo = datos.activa
        if datos.clave:
            cuenta.clave_hash = generar_hash_clave(datos.clave)
        repositorio.agregar(cuenta)
    hoy = (
        obtener_hora_utc()
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("America/Lima"))
        .date()
    )
    actuales = repositorio.asignaciones_abiertas(persona)
    if datos.horario_id != (actuales[-1].horario_id if actuales else None):
        for actual in actuales:
            if actual.vigente_desde == hoy:
                repositorio.eliminar(actual)
            else:
                actual.vigente_hasta = hoy - timedelta(days=1)
        repositorio.sincronizar()
        if datos.horario_id:
            repositorio.agregar(
                AsignacionHorario(
                    persona_id=persona.id,
                    horario_id=datos.horario_id,
                    vigente_desde=hoy,
                )
            )
    if repositorio.obtener_rol(datos.rol_id).codigo == "docente":
        tarifa = repositorio.tarifa_de_persona(persona) or TarifaDocente(
            persona_id=persona.id
        )
        tarifa.tarifa_hora = datos.tarifa_hora
        repositorio.agregar(tarifa)
    registrar_auditoria(
        repositorio,
        usuario,
        "guardar_persona",
        "personas",
        persona.id,
        {campo: valor for campo, valor in campos.items() if campo != "documento"},
    )
    confirmar(repositorio)
    return {"id": persona.id, "mensaje": "Persona guardada."}


def guardar_carrera(
    datos: DatosCarrera, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    sede = sede_usuario(repositorio, usuario)
    carrera = (
        repositorio.obtener_carrera(datos.id) if datos.id else Carrera(sede_id=sede)
    )
    if not carrera or carrera.sede_id != sede:
        raise ErrorAplicacion(404, "Carrera no disponible.")
    for campo, valor in datos.model_dump(exclude={"id"}).items():
        setattr(carrera, campo, valor)
    repositorio.agregar(carrera)
    try:
        repositorio.sincronizar()
    except ConflictoPersistencia:
        repositorio.revertir()
        raise ErrorAplicacion(409, "El código de carrera ya existe.")
    registrar_auditoria(
        repositorio,
        usuario,
        "guardar_carrera",
        "carreras",
        carrera.id,
        datos.model_dump(),
    )
    confirmar(repositorio)
    return {"mensaje": "Carrera guardada."}


def guardar_grupo(
    datos: DatosGrupo, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    sede = sede_usuario(repositorio, usuario)
    carrera = repositorio.obtener_carrera(datos.carrera_id)
    if not carrera or carrera.sede_id != sede:
        raise ErrorAplicacion(422, "Carrera no disponible.")
    if datos.horario_id:
        comprobar_horario(repositorio, sede, datos.horario_id)
    grupo = repositorio.obtener_grupo(datos.id) if datos.id else Grupo()
    if not grupo or (
        datos.id and repositorio.obtener_carrera(grupo.carrera_id).sede_id != sede
    ):
        raise ErrorAplicacion(404, "Grupo no disponible.")
    for campo, valor in datos.model_dump(exclude={"id"}).items():
        setattr(grupo, campo, valor)
    repositorio.agregar(grupo)
    try:
        repositorio.sincronizar()
    except ConflictoPersistencia:
        repositorio.revertir()
        raise ErrorAplicacion(409, "El código de grupo ya existe.")
    registrar_auditoria(
        repositorio, usuario, "guardar_grupo", "grupos", grupo.id, datos.model_dump()
    )
    confirmar(repositorio)
    return {"mensaje": "Grupo guardado."}


def guardar_horario(
    datos: DatosHorario, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    vistos = set()
    for tramo in datos.tramos:
        if tramo.hora_salida and tramo.hora_salida <= tramo.hora_entrada:
            raise ErrorAplicacion(422, "La salida debe ser posterior a la entrada.")
        clave = (tramo.dia_semana, tramo.hora_entrada)
        if clave in vistos:
            raise ErrorAplicacion(422, "Hay tramos repetidos.")
        vistos.add(clave)
    horario = Horario(nombre=datos.nombre, sede_id=sede_usuario(repositorio, usuario))
    repositorio.agregar(horario)
    repositorio.sincronizar()
    for tramo in datos.tramos:
        repositorio.agregar(TramoHorario(horario_id=horario.id, **tramo.model_dump()))
    registrar_auditoria(
        repositorio,
        usuario,
        "crear_horario",
        "horarios",
        horario.id,
        datos.model_dump(),
    )
    confirmar(repositorio)
    return {"mensaje": "Horario creado. Puedes asignarlo a personas o grupos."}


def intervalo(repositorio, usuario, desde, hasta):
    if hasta < desde or (hasta - desde).days > 61:
        raise ErrorAplicacion(422, "Selecciona un intervalo de hasta 62 días.")
    sede = repositorio.obtener_sede(sede_usuario(repositorio, usuario))
    zona = ZoneInfo(sede.zona_horaria)
    inicio = (
        datetime.combine(desde, time.min, zona)
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )
    fin = (
        datetime.combine(hasta + timedelta(days=1), time.min, zona)
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )
    return (sede, zona, inicio, fin)


def filas_diarias(repositorio, usuario, desde, hasta, persona_id=None, solo_marcados=False):
    sede, zona, inicio, fin = intervalo(repositorio, usuario, desde, hasta)
    personas = (repositorio.personas_con_marcados(sede, inicio, fin)
                if solo_marcados else repositorio.personas_del_diario(sede, persona_id))
    marcas = repositorio.marcados_del_intervalo(fin, inicio, sede, persona_id)
    por_dia = {}
    for marcado in marcas:
        dia = marcado.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(zona).date()
        por_dia.setdefault((marcado.persona_id, dia), []).append(marcado)
    feriados = {
        dia.fecha
        for dia in repositorio.dias_no_lectivos_del_intervalo(desde, hasta, sede)
    }
    justificaciones = {
        (dato.persona_id, dato.fecha): dato
        for dato in repositorio.justificaciones_aprobadas(desde, hasta, sede, persona_id)
    }
    ahora = obtener_hora_utc().replace(tzinfo=timezone.utc).astimezone(zona)
    regla = regla_sede(repositorio, sede.id)
    filas = []
    for numero in range((hasta - desde).days + 1):
        fecha = desde + timedelta(days=numero)
        for persona in personas:
            marcas_persona = por_dia.get((persona.id, fecha), [])
            if not persona.activa and (not marcas_persona):
                continue
            rol = repositorio.obtener_rol(
                marcas_persona[0].rol_id if marcas_persona else persona.rol_id
            )
            tramos = tramos_para(repositorio, persona, fecha)
            entrada = next(
                (marcado for marcado in marcas_persona if marcado.tipo == "entrada"),
                None,
            )
            salida = next(
                (marcado for marcado in marcas_persona if marcado.tipo == "salida"),
                None,
            )
            estado = (
                entrada.resultado
                or evaluar_manual(repositorio, persona, entrada.ocurrido_en, "entrada")
                if entrada
                else "Pendiente"
            )
            programadas = sum(
                (
                    (
                        datetime.combine(fecha, tramo.hora_salida)
                        - datetime.combine(fecha, tramo.hora_entrada)
                    ).total_seconds()
                    / 3600
                    for tramo in tramos
                    if tramo.hora_salida
                )
            )
            if fecha in feriados:
                programadas = 0
            minutos = 0
            if entrada and tramos:
                local = entrada.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(
                    zona
                )
                minutos = max(
                    0,
                    int(
                        (
                            local
                            - datetime.combine(fecha, tramos[0].hora_entrada, zona)
                        ).total_seconds()
                        // 60
                    ),
                )
            if not entrada:
                if fecha in feriados or not tramos:
                    estado = "No programado"
                elif ahora > datetime.combine(
                    fecha, tramos[0].hora_entrada, zona
                ) + timedelta(minutes=regla.limite_ausencia_minutos):
                    estado = "Falta"
            justificacion = justificaciones.get((persona.id, fecha))
            if justificacion and (
                justificacion.tipo == "falta"
                and estado == "Falta"
                or (justificacion.tipo == "tardanza" and estado == "Tardanza")
            ):
                estado = "Justificado"
            horas = (
                max(
                    0, (salida.ocurrido_en - entrada.ocurrido_en).total_seconds() / 3600
                )
                if entrada and salida
                else 0
            )
            grupo = (
                repositorio.obtener_grupo(persona.grupo_id)
                if persona.grupo_id
                else None
            )
            carrera = repositorio.obtener_carrera(grupo.carrera_id) if grupo else None
            filas.append(
                {
                    "persona_id": persona.id,
                    "codigo": persona.codigo,
                    "nombre": f"{persona.nombres} {persona.apellidos}",
                    "rol": rol.nombre,
                    "rol_codigo": rol.codigo,
                    "fecha": str(fecha),
                    "entrada": (
                        entrada.ocurrido_en.replace(tzinfo=timezone.utc).isoformat()
                        if entrada
                        else None
                    ),
                    "salida": (
                        salida.ocurrido_en.replace(tzinfo=timezone.utc).isoformat()
                        if salida
                        else None
                    ),
                    "estado": estado,
                    "minutos_tardanza": minutos,
                    "horas_programadas": round(programadas, 2),
                    "horas_permanencia": round(horas, 2),
                    "grupo": grupo.codigo if grupo else "",
                    "carrera": carrera.nombre if carrera else "",
                    "modalidad": entrada.modalidad if entrada else "",
                    "requiere_salida": rol.requiere_salida,
                }
            )
    return filas


def filas_marcadas(filas):
    return sorted(
        (fila for fila in filas if fila["entrada"] or fila["salida"]),
        key=lambda fila: (max(fila["entrada"] or "", fila["salida"] or ""), fila["persona_id"]),
        reverse=True,
    )


def consultar_diario(
    desde: date,
    hasta: date,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
    solo_marcados: bool = False,
):
    filas = filas_diarias(repositorio, usuario, desde, hasta, solo_marcados=solo_marcados)
    return filas_marcadas(filas) if solo_marcados else filas


def consultar_resumen(
    fecha: date, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    diario = filas_diarias(repositorio, usuario, fecha, fecha)
    semana = filas_diarias(repositorio, usuario, fecha - timedelta(days=6), fecha)
    pendientes = repositorio.justificaciones_pendientes(
        sede_usuario(repositorio, usuario)
    )
    return {
        "presentes": sum((fila["entrada"] is not None for fila in diario)),
        "tardanzas": sum((fila["estado"] == "Tardanza" for fila in diario)),
        "faltas": sum((fila["estado"] == "Falta" for fila in diario)),
        "pendientes": len(pendientes),
        "diario": filas_marcadas(diario),
        "semana": [
            {
                "fecha": str(fecha - timedelta(days=6 - numero)),
                "presentes": sum(
                    (
                        fila["entrada"] is not None
                        and fila["fecha"] == str(fecha - timedelta(days=6 - numero))
                        for fila in semana
                    )
                ),
            }
            for numero in range(7)
        ],
    }


def registrar_manual(
    datos: DatosManual, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    persona = comprobar_persona(repositorio, usuario, datos.persona_id)
    repositorio.bloquear_persona(persona)
    previo = repositorio.marcado_por_evento(datos)
    if previo:
        if previo.persona_id != persona.id or previo.registrado_por_id != usuario.id:
            raise ErrorAplicacion(409, "Ese identificador de registro ya existe.")
        return {"mensaje": "Registro ya guardado.", "id": previo.id}
    if not persona.activa:
        raise ErrorAplicacion(422, "La persona está desactivada.")
    sede = repositorio.obtener_sede(persona.sede_id)
    local = datos.fecha_hora
    if local.tzinfo is None:
        local = local.replace(tzinfo=ZoneInfo(sede.zona_horaria))
    instante = local.astimezone(timezone.utc).replace(tzinfo=None)
    if instante > obtener_hora_utc() + timedelta(seconds=30):
        raise ErrorAplicacion(422, "No puedes registrar una hora futura.")
    dia = local.astimezone(ZoneInfo(sede.zona_horaria)).date()
    _, _, inicio, fin = intervalo(repositorio, usuario, dia, dia)
    existentes = repositorio.marcados_de_persona(fin, inicio, persona)
    if any((marcado.tipo == datos.tipo for marcado in existentes)):
        raise ErrorAplicacion(409, "Ese movimiento ya está registrado para ese día.")
    if datos.tipo == "salida":
        if not repositorio.obtener_rol(persona.rol_id).requiere_salida:
            raise ErrorAplicacion(422, "Los estudiantes registran solamente entrada.")
        if not any(
            (
                marcado.tipo == "entrada" and marcado.ocurrido_en < instante
                for marcado in existentes
            )
        ):
            raise ErrorAplicacion(
                422, "Registra primero una entrada anterior a la salida."
            )
    from ...models import PuntoAsistencia

    punto = repositorio.primer_punto_de_sede(PuntoAsistencia, persona)
    resultado = evaluar_manual(repositorio, persona, instante, datos.tipo)
    marcado = Marcado(
        persona_id=persona.id,
        punto_id=punto.id,
        rol_id=persona.rol_id,
        tipo=datos.tipo,
        modalidad="manual",
        ocurrido_en=instante,
        registrado_por_id=usuario.id,
        motivo=datos.motivo.strip(),
        identificador_evento=datos.identificador_evento,
        resultado=resultado,
    )
    repositorio.agregar(marcado)
    repositorio.sincronizar()
    registrar_auditoria(
        repositorio,
        usuario,
        "registro_manual",
        "marcados",
        marcado.id,
        {"hora": instante, "motivo": datos.motivo},
    )
    sede_id = persona.sede_id
    confirmar(repositorio)
    notificar_marcado(sede_id)
    return {"mensaje": "Registro manual guardado.", "id": marcado.id}


def consultar_justificaciones(
    usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    filas = repositorio.justificaciones_de_sede(sede_usuario(repositorio, usuario))
    return [
        {
            **datos_objeto(justificacion),
            "nombre": f"{persona.nombres} {persona.apellidos}",
        }
        for justificacion, persona in filas
    ]


def crear_justificacion(
    datos: DatosJustificacion,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    comprobar_persona(repositorio, usuario, datos.persona_id)
    justificacion = Justificacion(**datos.model_dump(), creada_por_id=usuario.id)
    repositorio.agregar(justificacion)
    repositorio.sincronizar()
    registrar_auditoria(
        repositorio,
        usuario,
        "crear_justificacion",
        "justificaciones",
        justificacion.id,
        {"persona_id": datos.persona_id, "fecha": datos.fecha},
    )
    confirmar(repositorio)
    return {"mensaje": "Justificación registrada."}


def resolver_justificacion(
    identificador: int,
    datos: ResolverJustificacion,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    justificacion = repositorio.obtener_justificacion(identificador)
    if not justificacion:
        raise ErrorAplicacion(404, "Justificación no disponible.")
    comprobar_persona(repositorio, usuario, justificacion.persona_id)
    anterior = justificacion.estado
    justificacion.estado, justificacion.observacion, justificacion.resuelta_por_id = (
        datos.estado,
        datos.observacion,
        usuario.id,
    )
    registrar_auditoria(
        repositorio,
        usuario,
        "resolver_justificacion",
        "justificaciones",
        justificacion.id,
        {"anterior": anterior, **datos.model_dump()},
    )
    confirmar(repositorio)
    return {"mensaje": "Estado actualizado."}


def guardar_reglas(
    datos: DatosReglas, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    if datos.alerta_porcentaje <= datos.observacion_porcentaje:
        raise ErrorAplicacion(
            422, "El umbral de alerta debe superar el de observación."
        )
    hoy = (
        obtener_hora_utc()
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("America/Lima"))
        .date()
    )
    for identificador, minutos in datos.tolerancias.items():
        if not repositorio.obtener_rol(identificador) or not 0 <= minutos <= 1440:
            raise ErrorAplicacion(422, "Revisa los roles y sus minutos de tolerancia.")
        margen = repositorio.bloquear_tolerancia(hoy, identificador)
        if margen and margen.vigente_desde == hoy:
            margen.minutos = minutos
        else:
            if margen:
                margen.vigente_hasta = hoy - timedelta(days=1)
            repositorio.agregar(
                ToleranciaRol(rol_id=identificador, minutos=minutos, vigente_desde=hoy)
            )
    regla = regla_sede(repositorio, sede_usuario(repositorio, usuario))
    for campo, valor in datos.model_dump(exclude={"tolerancias"}).items():
        setattr(regla, campo, valor)
    repositorio.agregar(regla)
    repositorio.sincronizar()
    registrar_auditoria(
        repositorio,
        usuario,
        "guardar_reglas",
        "reglas_sedes",
        regla.id,
        datos.model_dump(),
    )
    confirmar(repositorio)
    return {
        "mensaje": "Reglas guardadas. Los marcados previos conservan su resultado original."
    }


def guardar_dia(
    datos: DatosDia, usuario: Usuario = None, repositorio: RepositorioGestion = None
):
    sede = sede_usuario(repositorio, usuario)
    dia = repositorio.dia_no_lectivo(datos, sede) or DiaNoLectivo(
        sede_id=sede, fecha=datos.fecha
    )
    dia.motivo = datos.motivo
    repositorio.agregar(dia)
    repositorio.sincronizar()
    registrar_auditoria(
        repositorio,
        usuario,
        "guardar_dia_no_lectivo",
        "dias_no_lectivos",
        dia.id,
        datos.model_dump(),
    )
    confirmar(repositorio)
    return {"mensaje": "Día no lectivo guardado."}


def guardar_dispositivo(
    datos: DatosDispositivo,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    if datos.direccion_ip:
        try:
            ip_address(datos.direccion_ip)
        except ValueError:
            raise ErrorAplicacion(422, "Escribe una dirección IP válida.")
    sede = sede_usuario(repositorio, usuario)
    dispositivo = (
        repositorio.obtener_dispositivo(datos.id)
        if datos.id
        else Dispositivo(sede_id=sede)
    )
    if not dispositivo or dispositivo.sede_id != sede:
        raise ErrorAplicacion(404, "Dispositivo no disponible.")
    for campo, valor in datos.model_dump(exclude={"id"}).items():
        setattr(dispositivo, campo, valor)
    repositorio.agregar(dispositivo)
    repositorio.sincronizar()
    registrar_auditoria(
        repositorio,
        usuario,
        "guardar_dispositivo",
        "dispositivos",
        dispositivo.id,
        datos.model_dump(),
    )
    confirmar(repositorio)
    return {
        "mensaje": "Configuración guardada. Los biométricos no están conectados en esta demo."
    }


def consultar_expediente(
    identificador: int,
    desde: date,
    hasta: date,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    persona = comprobar_persona(repositorio, usuario, identificador)
    valor = f"fym:carne:{persona.id}:{persona.version_carne}"
    filas = [
        fila
        for fila in filas_diarias(repositorio, usuario, desde, hasta)
        if fila["persona_id"] == persona.id
    ]
    programados = [
        fila for fila in filas if fila["estado"] not in ("No programado", "Pendiente")
    ]
    faltas = sum((fila["estado"] == "Falta" for fila in programados))
    porcentaje = round(faltas * 100 / len(programados), 1) if programados else 0
    regla = regla_sede(repositorio, persona.sede_id)
    alerta = (
        "Alerta"
        if porcentaje >= regla.alerta_porcentaje
        else "Observación" if porcentaje >= regla.observacion_porcentaje else "Regular"
    )
    return {
        "persona": {
            "nombre": f"{persona.nombres} {persona.apellidos}",
            "codigo": persona.codigo,
            "rol": repositorio.obtener_rol(persona.rol_id).nombre,
            "iniciales": iniciales_persona(persona),
            "sede": repositorio.obtener_sede(persona.sede_id).nombre,
            "qr": valor + ":" + firmar(valor),
        },
        "calendario": filas,
        "faltas": faltas,
        "porcentaje_faltas": porcentaje,
        "alerta": alerta,
        "tramos": [
            datos_objeto(tramo) for tramo in tramos_para(repositorio, persona, hasta)
        ],
    }


def consultar_preplanilla(
    desde: date,
    hasta: date,
    tarifa: Decimal | None = None,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    if tarifa is not None and (not 0 <= tarifa <= 100000):
        raise ErrorAplicacion(422, "La tarifa debe estar entre 0 y 100000.")
    filas = filas_diarias(repositorio, usuario, desde, hasta)
    docentes = repositorio.docentes_de_sede(sede_usuario(repositorio, usuario))
    resultados = []
    for docente in docentes:
        datos = [fila for fila in filas if fila["persona_id"] == docente.id]
        configurada = repositorio.tarifa_del_docente(docente)
        valor = (
            tarifa
            if tarifa is not None
            else Decimal(configurada.tarifa_hora) if configurada else Decimal(0)
        )
        horas = sum((fila["horas_permanencia"] for fila in datos))
        minutos = sum(
            (fila["minutos_tardanza"] for fila in datos if fila["estado"] == "Tardanza")
        )
        resultados.append(
            {
                "persona_id": docente.id,
                "nombre": f"{docente.nombres} {docente.apellidos}",
                "horas_programadas": round(
                    sum((fila["horas_programadas"] for fila in datos)), 2
                ),
                "horas_permanencia": round(horas, 2),
                "minutos_tardanza": minutos,
                "faltas": sum((fila["estado"] == "Falta" for fila in datos)),
                "dias_incompletos": sum(
                    (
                        fila["entrada"] is not None and fila["salida"] is None
                        for fila in datos
                    )
                ),
                "tarifa_hora": float(valor),
                "importe_estimado": round(float(valor) * horas, 2),
                "descuento_referencial": round(float(valor) * minutos / 60, 2),
            }
        )
    return resultados


def exportar(
    desde: date,
    hasta: date,
    tipo: Literal["asistencia", "preplanilla"] = "asistencia",
    rol: str = "",
    buscar: str = "",
    estado: str = "",
    carrera: str = "",
    tarifa: Decimal | None = None,
    solo_marcados: bool = False,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    if tipo == "preplanilla":
        if usuario.permiso != "administrador":
            raise ErrorAplicacion(
                403, "La preplanilla requiere permiso de administrador."
            )
        filas = consultar_preplanilla(desde, hasta, tarifa, usuario, repositorio)
    else:
        filas = [
            fila
            for fila in consultar_diario(desde, hasta, usuario, repositorio, solo_marcados=solo_marcados)
            if (not rol or fila["rol_codigo"] == rol)
            and (not estado or fila["estado"] == estado)
            and (not carrera or fila["carrera"] == carrera)
            and (
                not buscar
                or buscar.lower() in (fila["nombre"] + fila["codigo"]).lower()
            )
        ]
    return construir_excel(filas, tipo)


def consultar_historial_marcados(
    desde: date,
    hasta: date,
    usuario: Usuario = None,
    repositorio: RepositorioGestion = None,
):
    sede, zona, inicio, fin = intervalo(repositorio, usuario, desde, hasta)
    filas = repositorio.historial_de_marcados(fin, inicio, sede)
    return [
        {
            "id": marcado.id,
            "persona_id": persona.id,
            "nombre": f"{persona.nombres} {persona.apellidos}",
            "codigo": persona.codigo,
            "tipo": marcado.tipo,
            "fecha": str(
                marcado.ocurrido_en.replace(tzinfo=timezone.utc).astimezone(zona).date()
            ),
            "hora": marcado.ocurrido_en.replace(tzinfo=timezone.utc).isoformat(),
            "cargado_en": marcado.registrado_en.replace(
                tzinfo=timezone.utc
            ).isoformat(),
            "responsable": responsable or "Marcado personal",
            "modalidad": marcado.modalidad,
            "motivo": marcado.motivo,
            "resultado": marcado.resultado
            or evaluar_manual(repositorio, persona, marcado.ocurrido_en, marcado.tipo),
        }
        for marcado, persona, responsable in filas
    ]
