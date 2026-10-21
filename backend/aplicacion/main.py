from fastapi import FastAPI
from .version import VERSION
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from .compartido.errores import ErrorAplicacion, ConflictoPersistencia
from pathlib import Path
from .modulos.acceso.rutas import rutas
from .modulos.asistencia.rutas import rutas_asistencia
from .modulos.gestion.rutas import rutas_gestion
from .modulos.diagnostico.rutas import rutas_salud, rutas_diagnostico

aplicacion = FastAPI(
    title="FyM Pass", description="API de asistencia institucional", version=VERSION
)
for enrutador in (
    rutas_salud,
    rutas,
    rutas_asistencia,
    rutas_gestion,
    rutas_diagnostico,
):
    aplicacion.include_router(enrutador)


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
