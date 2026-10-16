from io import BytesIO
from pathlib import Path
from uuid import uuid4
from PIL import Image, UnidentifiedImageError
from ..compartido.errores import ErrorAplicacion

CARPETA_FOTOS = Path(__file__).resolve().parents[2] / "archivos/fotos"


def guardar_foto_validada(contenido):
    if len(contenido) > 3 * 1024 * 1024:
        raise ErrorAplicacion(422, "La foto debe ocupar menos de 3 MB.")
    try:
        foto = Image.open(BytesIO(contenido))
        if foto.width > 4096 or foto.height > 4096:
            raise ValueError()
        foto = foto.convert("RGB")
        foto.thumbnail((512, 512))
    except (UnidentifiedImageError, ValueError, OSError):
        raise ErrorAplicacion(
            422, "Selecciona una imagen JPG o PNG válida de hasta 4096 píxeles."
        )
    CARPETA_FOTOS.mkdir(parents=True, exist_ok=True)
    nombre = str(uuid4()) + ".jpg"
    foto.save(CARPETA_FOTOS / nombre, format="JPEG", quality=85)
    return "/api/fotos/" + nombre
