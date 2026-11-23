"""copia un respaldo cifrado a google drive y comprueba su integridad"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from .administrar_seguridad import respaldo


def resumen_md5(archivo: Path) -> str:
    calculo = hashlib.md5()
    with archivo.open("rb") as origen:
        for bloque in iter(lambda: origen.read(1024 * 1024), b""):
            calculo.update(bloque)
    return calculo.hexdigest()


def main():
    destino = os.environ.get("FYM_RESPALDO_REMOTO", "").strip().rstrip("/")
    configuracion = os.environ.get("RCLONE_CONFIG", "").strip()
    if not destino or ":" not in destino or not configuracion:
        raise RuntimeError("Configura FYM_RESPALDO_REMOTO y RCLONE_CONFIG antes de iniciar el respaldo.")
    archivo_configuracion = Path(configuracion)
    if not archivo_configuracion.is_file():
        raise RuntimeError("No se encontró la configuración privada de rclone.")
    ejecutable = shutil.which("rclone")
    if not ejecutable:
        raise RuntimeError("Instala rclone desde su fuente oficial antes de programar respaldos.")

    archivo = respaldo()
    remoto = f"{destino}/{archivo.name}"
    subprocess.run([ejecutable, "copyto", str(archivo), remoto, "--checksum", "--config", str(archivo_configuracion)], check=True)
    listado = subprocess.run(
        [ejecutable, "lsjson", remoto, "--stat", "--hash", "--config", str(archivo_configuracion)],
        check=True, capture_output=True, text=True,
    )
    datos = json.loads(listado.stdout)
    if datos.get("Size") != archivo.stat().st_size or datos.get("Hashes", {}).get("MD5", "").lower() != resumen_md5(archivo):
        raise RuntimeError("El respaldo remoto no coincide con el archivo cifrado local.")
    print("Respaldo cifrado confirmado en Drive:", archivo.name)


if __name__ == "__main__":
    main()
