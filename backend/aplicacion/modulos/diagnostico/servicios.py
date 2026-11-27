from ...version import VERSION
from ...compartido.errores import FalloPersistencia


def consultar_salud():
    return {"estado": "disponible", "aplicacion": "FyM Pass", "version": VERSION}


def consultar_base_datos(repositorio):
    try:
        version = repositorio.version_base()
        return {
            "estado": "disponible",
            "motor": "MariaDB" if "mariadb" in version.lower() else "MySQL",
            "version": version,
        }
    except FalloPersistencia:
        return {
            "estado": "sin conexion",
            "mensaje": "Revisa el servicio de base de datos y la configuración del backend.",
        }
