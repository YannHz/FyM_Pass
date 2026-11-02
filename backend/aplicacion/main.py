from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging
from .version import VERSION
from .config import configuracion
from .compartido.errores import ErrorAplicacion, ConflictoPersistencia
from pathlib import Path
from .modulos.acceso.rutas import rutas
from .modulos.asistencia.rutas import rutas_asistencia
from .modulos.gestion.rutas import rutas_gestion
from .modulos.diagnostico.rutas import rutas_salud, rutas_diagnostico

avisos_registro = logging.getLogger("fym")


@asynccontextmanager
async def vigilar_configuracion(aplicacion_en_uso):
    # avisa al arrancar sobre configuracion debil antes del despliegue
    if len(configuracion.clave_qr) < 32:
        avisos_registro.warning(
            "CLAVE_QR ausente o corta: los codigos QR no se validarán hasta configurar una clave de 32 caracteres o más."
        )
    if not configuracion.cookie_segura:
        avisos_registro.warning(
            "COOKIE_SEGURA=false: da la cookie sin Secure. Definela antes de servir por HTTPS en producción."
        )
    yield


aplicacion = FastAPI(
    title="FyM Pass",
    description="API de asistencia institucional",
    version=VERSION,
    lifespan=vigilar_configuracion,
)
for enrutador in (
    rutas_salud,
    rutas,
    rutas_asistencia,
    rutas_gestion,
    rutas_diagnostico,
):
    aplicacion.include_router(enrutador)


@aplicacion.middleware("http")
async def encabezados_seguridad(request, siguiente):
    respuesta = await siguiente(request)
    respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
    respuesta.headers.setdefault("X-Frame-Options", "DENY")
    respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if configuracion.cookie_segura:
        respuesta.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000"
        )
    return respuesta


@aplicacion.exception_handler(ErrorAplicacion)
async def manejar_error_aplicacion(request, error):
    return JSONResponse(status_code=error.codigo, content={"detail": error.mensaje})


@aplicacion.exception_handler(SQLAlchemyError)
@aplicacion.exception_handler(ConflictoPersistencia)
async def manejar_error_base_datos(request, error):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "No se pudo guardar o consultar el registro. Revisa la conexión con la base de datos."
        },
    )


CARPETA_FOTOS = Path(__file__).resolve().parents[1] / "archivos/fotos"
CARPETA_FOTOS.mkdir(parents=True, exist_ok=True)
aplicacion.mount("/api/fotos", StaticFiles(directory=CARPETA_FOTOS), name="fotos")
