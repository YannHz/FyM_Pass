from pathlib import Path
import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import motor
from .models import Persona, Usuario
from .seguridad import generar_hash_clave


def crear_datos_demo():
    ruta = Path(__file__).resolve().parents[1] / ".credenciales_demo.local.txt"
    if ruta.exists():
        print("Las credenciales demo ya existen; no se modificaron cuentas.")
        return
    cuentas = [("admin.demo", "DEMO-ADM-01", "Ana", "Demo", 3, "administrador"),
        ("operador.demo", "DEMO-ADM-02", "Luis", "Demo", 3, "operador"),
        ("docente.demo", "DEMO-DOC-01", "Elena", "Demo", 2, "personal"),
        ("estudiante.demo", "DEMO-EST-01", "Diego", "Demo", 1, "personal")]
    lineas = ["Credenciales locales de demostración de FyM Pass. No publicar."]
    with Session(motor) as base:
        for nombre, codigo, nombres, apellidos, rol, permiso in cuentas:
            if base.scalar(select(Usuario).where(Usuario.nombre_usuario == nombre)):
                raise RuntimeError("Hay una cuenta demo existente; se conserva sin cambios.")
            persona = Persona(codigo=codigo, nombres=nombres, apellidos=apellidos, rol_id=rol, sede_id=1)
            base.add(persona)
            base.flush()
            clave = secrets.token_urlsafe(12)
            base.add(Usuario(persona_id=persona.id, nombre_usuario=nombre, clave_hash=generar_hash_clave(clave), permiso=permiso))
            lineas.append(f"{nombre}: {clave}")
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        base.commit()
    print("Creadas 4 cuentas. Consulta las contraseñas en backend/.credenciales_demo.local.txt")


if __name__ == "__main__":
    crear_datos_demo()
