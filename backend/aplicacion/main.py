from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .database import motor

aplicacion = FastAPI(title="FyM Pass", description="API de asistencia institucional", version="0.1.0")

@aplicacion.get("/api/salud")
def consultar_salud():
    return {"estado": "disponible", "aplicacion": "FyM Pass", "version": "0.1.0"}

@aplicacion.get("/api/salud/base-datos")
def consultar_base_datos():
    try:
        with motor.connect() as conexion:
            version = conexion.execute(text("SELECT VERSION()")).scalar_one()
        return {"estado": "disponible", "motor": "MariaDB" if "mariadb" in version.lower() else "MySQL", "version": version}
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"estado": "sin conexion", "mensaje": "Revisa el servicio de XAMPP y la configuracion local del backend."})

from .acceso import rutas
aplicacion.include_router(rutas)

from .asistencia import rutas_asistencia
aplicacion.include_router(rutas_asistencia)

@aplicacion.exception_handler(SQLAlchemyError)
async def manejar_error_base_datos(request, error):
    return JSONResponse(status_code=503, content={"detail": "No se pudo guardar o consultar el registro. Revisa la conexión con la base de datos."})

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .gestion import rutas_gestion
aplicacion.include_router(rutas_gestion)
carpeta_fotos = Path(__file__).resolve().parents[1] / 'archivos/fotos'
carpeta_fotos.mkdir(parents=True, exist_ok=True)
aplicacion.mount('/api/fotos', StaticFiles(directory=carpeta_fotos), name='fotos')

from .diagnostico import rutas_diagnostico
aplicacion.include_router(rutas_diagnostico)
