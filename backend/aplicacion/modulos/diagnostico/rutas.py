from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from ...compartido.dependencias import obtener_base_datos, obtener_encargado
from .repositorio import RepositorioDiagnostico
from . import servicios

rutas_salud = APIRouter()


@rutas_salud.get("/api/salud")
def consultar_salud():
    return servicios.consultar_salud()


@rutas_salud.get("/api/salud/base-datos")
def consultar_base_datos(
    respuesta: Response,
    usuario: object = Depends(obtener_encargado),
    base: Session = Depends(obtener_base_datos),
):
    # solo encargados: no divulga motor y version al publico
    datos = servicios.consultar_base_datos(RepositorioDiagnostico(base))
    if datos["estado"] != "disponible":
        respuesta.status_code = 503
    return datos
