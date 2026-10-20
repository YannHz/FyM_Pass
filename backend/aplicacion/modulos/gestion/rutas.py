from datetime import date
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ...models import Usuario
from ...compartido.dependencias import (
    obtener_base_datos,
    obtener_encargado,
    validar_peticion,
    administrador,
)
from .repositorio import RepositorioGestion
from . import servicios
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

rutas_gestion = APIRouter(prefix="/api/gestion", tags=["Administración"])


@rutas_gestion.get("/catalogo")
def consultar_catalogo(
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_catalogo(
        usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/personas", dependencies=[Depends(validar_peticion)])
def guardar_persona(
    datos: DatosPersona,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_persona(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/carreras", dependencies=[Depends(validar_peticion)])
def guardar_carrera(
    datos: DatosCarrera,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_carrera(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/grupos", dependencies=[Depends(validar_peticion)])
def guardar_grupo(
    datos: DatosGrupo,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_grupo(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/horarios", dependencies=[Depends(validar_peticion)])
def guardar_horario(
    datos: DatosHorario,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_horario(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.get("/diario")
def consultar_diario(
    desde: date,
    hasta: date,
    respuesta: Response,
    solo_marcados: bool = False,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    respuesta.headers["Cache-Control"] = "no-store"
    return servicios.consultar_diario(
        desde=desde, hasta=hasta, solo_marcados=solo_marcados, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.get("/resumen")
def consultar_resumen(
    fecha: date,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_resumen(
        fecha=fecha, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/manual", dependencies=[Depends(validar_peticion)])
def registrar_manual(
    datos: DatosManual,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.registrar_manual(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.get("/justificaciones")
def consultar_justificaciones(
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_justificaciones(
        usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/justificaciones", dependencies=[Depends(validar_peticion)])
def crear_justificacion(
    datos: DatosJustificacion,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.crear_justificacion(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post(
    "/justificaciones/{identificador}/resolver",
    dependencies=[Depends(validar_peticion)],
)
def resolver_justificacion(
    identificador: int,
    datos: ResolverJustificacion,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.resolver_justificacion(
        identificador=identificador,
        datos=datos,
        usuario=usuario,
        repositorio=RepositorioGestion(base),
    )


@rutas_gestion.post("/reglas", dependencies=[Depends(validar_peticion)])
def guardar_reglas(
    datos: DatosReglas,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_reglas(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/dias-no-lectivos", dependencies=[Depends(validar_peticion)])
def guardar_dia(
    datos: DatosDia,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_dia(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.post("/dispositivos", dependencies=[Depends(validar_peticion)])
def guardar_dispositivo(
    datos: DatosDispositivo,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.guardar_dispositivo(
        datos=datos, usuario=usuario, repositorio=RepositorioGestion(base)
    )


@rutas_gestion.get("/personas/{identificador}/expediente")
def consultar_expediente(
    identificador: int,
    desde: date,
    hasta: date,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_expediente(
        identificador=identificador,
        desde=desde,
        hasta=hasta,
        usuario=usuario,
        repositorio=RepositorioGestion(base),
    )


@rutas_gestion.get("/preplanilla")
def consultar_preplanilla(
    desde: date,
    hasta: date,
    tarifa: Decimal | None = None,
    usuario: Usuario = Depends(administrador),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_preplanilla(
        desde=desde,
        hasta=hasta,
        tarifa=tarifa,
        usuario=usuario,
        repositorio=RepositorioGestion(base),
    )


@rutas_gestion.get("/exportar")
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
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    archivo = servicios.exportar(
        desde=desde,
        hasta=hasta,
        tipo=tipo,
        rol=rol,
        buscar=buscar,
        estado=estado,
        carrera=carrera,
        tarifa=tarifa,
        solo_marcados=solo_marcados,
        usuario=usuario,
        repositorio=RepositorioGestion(base),
    )
    return StreamingResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="FyM_{tipo}_{desde}_{hasta}.xlsx"'
        },
    )


@rutas_gestion.get("/marcados")
def consultar_historial_marcados(
    desde: date,
    hasta: date,
    usuario: Usuario = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    return servicios.consultar_historial_marcados(
        desde=desde, hasta=hasta, usuario=usuario, repositorio=RepositorioGestion(base)
    )
