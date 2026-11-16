from argparse import ArgumentParser
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo
import os
import unicodedata
import shutil
import subprocess
from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session
from .config import configuracion
from .version import VERSION
from .database import motor
from .models import (
    Persona,
    Usuario,
    Rol,
    Sede,
    Carrera,
    Grupo,
    Horario,
    TramoHorario,
    AsignacionHorario,
    ToleranciaRol,
    TarifaDocente,
    EventoPuesto,
    Marcado,
    Justificacion,
    Auditoria,
    PuestoAbierto,
    SesionAcceso,
)
from .seguridad import generar_hash_clave
from .compartido.credenciales import credenciales_iniciales

ADMINISTRATIVOS = [
    ("María Elena", "Salazar Rojas", "mariasalazar", "administrador"),
    ("Ana Isabel", "Mendoza Paredes", "anamendoza", "administrador"),
    ("Rosa Patricia", "Quispe Torres", "rosaquispe", "operador"),
    ("Carla Beatriz", "Vargas Medina", "carlavargas", "operador"),
    ("Lucía Fernanda", "Ramos Flores", "luciaramos", "operador"),
    ("Elena Victoria", "Castro Pérez", "elenacastro", "operador"),
]
DOCENTES = [
    ("Luis Fernando", "Huamán Castro", "luishuaman"),
    ("Ana Lucía", "Gutiérrez Flores", "anagutierrez"),
    ("Miguel Ángel", "Ramos Cárdenas", "miguelramos"),
    ("Patricia Isabel", "Díaz Herrera", "patriciadiaz"),
    ("José Antonio", "Pérez Valdivia", "joseperez"),
    ("Claudia Milagros", "Sánchez León", "claudiasanchez"),
    ("Roberto Carlos", "Vega Torres", "robertovega"),
    ("Diana Mercedes", "Flores Rojas", "dianaflores"),
    ("Javier Alonso", "Medina Quispe", "javiermedina"),
    ("Teresa Beatriz", "Castro Salas", "teresacastro"),
]

def reemplazar_personas(base):
    # conserva los catalogos y retira primero las referencias a las cuentas antiguas
    for modelo in (
        EventoPuesto,
        Justificacion,
        Auditoria,
        Marcado,
        PuestoAbierto,
        SesionAcceso,
        Usuario,
        TarifaDocente,
        AsignacionHorario,
        Persona,
    ):
        base.execute(delete(modelo))
    horarios_demo = select(Horario.id).where(Horario.nombre.like("DEMO -%"))
    usados = select(Grupo.horario_id).where(Grupo.horario_id.is_not(None))
    identificadores = list(base.scalars(horarios_demo.where(Horario.id.not_in(usados))))
    if identificadores:
        base.execute(
            delete(TramoHorario).where(TramoHorario.horario_id.in_(identificadores))
        )
        base.execute(delete(Horario).where(Horario.id.in_(identificadores)))


def crear_personas_iniciales(base, inicio):
    if base.scalar(select(func.count()).select_from(Persona)) or base.scalar(
        select(func.count()).select_from(Usuario)
    ):
        raise RuntimeError(
            "La carga inicial requiere personas y cuentas vacías. No se modificaron los datos."
        )
    sede = base.scalar(select(Sede).where(Sede.activa.is_(True)).order_by(Sede.id))
    if sede is None:
        raise RuntimeError(
            "Primero aplica las migraciones para crear la sede y los roles."
        )
    roles = {rol.codigo: rol.id for rol in base.scalars(select(Rol))}
    if not {"administrativo", "docente"}.issubset(roles):
        raise RuntimeError("Faltan los roles institucionales requeridos.")
    horarios = {}
    for codigo, nombre, entrada, salida in [
        ("administracion", "Administración · 08:00 a 17:00", 8, 17),
        ("docentes_manana", "Docentes · mañana 08:00 a 13:00", 8, 13),
        ("docentes_tarde", "Docentes · tarde 14:00 a 19:00", 14, 19),
    ]:
        horario = base.scalar(
            select(Horario).where(Horario.sede_id == sede.id, Horario.nombre == nombre)
        )
        if horario is None:
            horario = Horario(nombre=nombre, sede_id=sede.id,
                tipo_personal="docente" if codigo.startswith("docentes") else "administrativo",
                turno="tarde" if codigo.endswith("tarde") else "manana" if codigo.startswith("docentes") else "completo")
            base.add(horario)
            base.flush()
            for dia in range(5):
                base.add(
                    TramoHorario(
                        horario_id=horario.id,
                        dia_semana=dia,
                        hora_entrada=time(entrada),
                        hora_salida=time(salida) if salida else None,
                    )
                )
        horarios[codigo] = horario.id
    for rol in roles.values():
        if (
            base.scalar(
                select(ToleranciaRol).where(
                    ToleranciaRol.rol_id == rol,
                    ToleranciaRol.vigente_desde <= inicio,
                    (
                        ToleranciaRol.vigente_hasta.is_(None)
                        | (ToleranciaRol.vigente_hasta >= inicio)
                    ),
                )
            )
            is None
        ):
            base.add(ToleranciaRol(rol_id=rol, minutos=10, vigente_desde=inicio))
    cuentas = []

    def agregar(nombres, apellidos, usuario, rol, permiso, codigo, horario, grupo=None):
        persona = Persona(
            codigo=codigo,
            nombres=nombres,
            apellidos=apellidos,
            sede_id=sede.id,
            rol_id=roles[rol],
            grupo_id=grupo,
        )
        base.add(persona)
        base.flush()
        usuario, clave = credenciales_iniciales(nombres, apellidos,
            lambda nombre: base.scalar(select(Usuario.id).where(Usuario.nombre_usuario == nombre)) is None)
        base.add(
            Usuario(
                persona_id=persona.id,
                nombre_usuario=usuario,
                clave_hash=generar_hash_clave(clave),
                permiso=permiso,
            )
        )
        base.add(
            AsignacionHorario(
                persona_id=persona.id, horario_id=horario, vigente_desde=inicio
            )
        )
        cuentas.append(
            {
                "nombre": f"{nombres} {apellidos}",
                "usuario": usuario,
                "clave": clave,
                "rol": rol,
                "permiso": permiso,
                "codigo": codigo,
            }
        )

    for numero, (nombres, apellidos, usuario, permiso) in enumerate(ADMINISTRATIVOS, 1):
        agregar(
            nombres,
            apellidos,
            usuario,
            "administrativo",
            permiso,
            f"ADM-{numero:04}",
            horarios["administracion"],
        )
    for numero, (nombres, apellidos, usuario) in enumerate(DOCENTES, 1):
        agregar(
            nombres,
            apellidos,
            usuario,
            "docente",
            "personal",
            f"DOC-{numero:04}",
            horarios["docentes_manana" if numero <= 5 else "docentes_tarde"],
        )
    base.flush()
    return cuentas


def respaldar_base(carpeta):
    ejecutable = shutil.which("mariadb-dump") or shutil.which("mysqldump")
    if not ejecutable and Path("C:/xampp/mysql/bin/mysqldump.exe").exists():
        ejecutable = "C:/xampp/mysql/bin/mysqldump.exe"
    if not ejecutable:
        raise RuntimeError(
            "Instala mysqldump o mariadb-dump antes de reemplazar los usuarios."
        )
    destino = carpeta / "antes_de_beta.sql"
    entorno = dict(os.environ, MYSQL_PWD=configuracion.bd_clave)
    resultado = subprocess.run(
        [
            ejecutable,
            "--host",
            configuracion.bd_host,
            "--port",
            str(configuracion.bd_puerto),
            "--user",
            configuracion.bd_usuario,
            "--single-transaction",
            "--skip-lock-tables",
            "--hex-blob",
            "--result-file",
            str(destino),
            configuracion.bd_nombre,
        ],
        env=entorno,
        capture_output=True,
    )
    if resultado.returncode or not destino.exists() or destino.stat().st_size == 0:
        raise RuntimeError(
            "No se pudo completar el respaldo. No se modificaron los datos."
        )
    return destino


def guardar_listado(cuentas, archivo, respaldo, inicio):
    lineas = [
        "# Accesos privados · FyM Pass",
        "",
        "Personas completamente ficticias para pruebas. No publicar este archivo.",
        "",
        f"Versión: {VERSION}. Usuarios sin puntos. Contraseña: primer nombre en minúsculas sin tildes + fym.",
        "",
        "| Persona | Usuario | Contraseña | Rol | Permiso |",
        "| --- | --- | --- | --- | --- |",
    ]
    for cuenta in cuentas:
        lineas.append(
            "| "
            + " | ".join(
                cuenta[campo]
                for campo in ["nombre", "usuario", "clave", "rol", "permiso"]
            )
            + " |"
        )
    lineas += [
        "",
        "## Base local",
        "",
        f"Host: {configuracion.bd_host}",
        f"Puerto: {configuracion.bd_puerto}",
        f"Base: {configuracion.bd_nombre}",
        f"Usuario: {configuracion.bd_usuario}",
        f"Contraseña: {configuracion.bd_clave}",
        "",
        "Horarios ficticios de lunes a viernes; administración 08–17 y docentes 08–13 o 14–19. Inicio de vigencia: "
        + inicio.isoformat(),
        "",
        "Respaldo anterior: " + str(respaldo),
    ]
    archivo.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def preparar_datos_iniciales(reemplazar=False, confirmar_base=""):
    if configuracion.bd_host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Esta herramienta está limitada a la base local de pruebas.")
    if confirmar_base != configuracion.bd_nombre:
        raise RuntimeError(
            "Indica --confirmar-base con el nombre exacto de la base local."
        )
    raiz = Path(__file__).resolve().parents[2]
    momento = datetime.now(ZoneInfo("America/Lima"))
    carpeta = (
        raiz / "backend/archivos/respaldos" / momento.strftime("beta_%Y%m%d_%H%M%S_%f")
    )
    carpeta.mkdir(parents=True, exist_ok=False)
    respaldo = respaldar_base(carpeta)
    for nombre in [
        "README_CREDENCIALES.local.md",
        "backend/.credenciales_demo.local.txt",
        "backend/.credenciales_beta.local.txt",
    ]:
        anterior = raiz / nombre
        if anterior.exists():
            shutil.copy2(anterior, carpeta / anterior.name)
    archivo = carpeta / "credenciales_beta.local.md"
    with Session(motor) as base:
        with base.begin():
            existentes = base.scalar(select(func.count()).select_from(Usuario))
            if existentes and not reemplazar:
                raise RuntimeError(
                    "Hay usuarios. Usa --reemplazar-usuarios para reemplazarlos con respaldo."
                )
            if reemplazar:
                reemplazar_personas(base)
            cuentas = crear_personas_iniciales(base, momento.date())
            guardar_listado(cuentas, archivo, respaldo, momento.date())
        # conserva una copia recuperable incluso si falla la escritura del acceso rapido
        shutil.copy2(archivo, raiz / "README_CREDENCIALES.local.md")
        (raiz / "backend/.credenciales_beta.local.txt").write_text(
            "\n".join(f"{cuenta['usuario']}: {cuenta['clave']}" for cuenta in cuentas)
            + "\n",
            encoding="utf-8",
        )
        anterior_demo = raiz / "backend/.credenciales_demo.local.txt"
        if anterior_demo.exists():
            anterior_demo.unlink()
    print(
        f"Beta local preparada: {len(cuentas)} cuentas ficticias. No se generaron asistencias."
    )
    print("Credenciales: README_CREDENCIALES.local.md")
    print("Respaldo privado:", respaldo)
    return cuentas


def actualizar_accesos_iniciales(confirmar_base):
    if (
        configuracion.bd_host not in {"127.0.0.1", "localhost", "::1"}
        or confirmar_base != configuracion.bd_nombre
    ):
        raise RuntimeError(
            "Confirma el nombre de la base local antes de actualizar accesos."
        )
    raiz = Path(__file__).resolve().parents[2]
    momento = datetime.now(ZoneInfo("America/Lima"))
    carpeta = (
        raiz
        / "backend/archivos/respaldos"
        / momento.strftime("accesos_%Y%m%d_%H%M%S_%f")
    )
    carpeta.mkdir(parents=True, exist_ok=False)
    respaldo = respaldar_base(carpeta)
    for nombre in [
        "README_CREDENCIALES.local.md",
        "backend/.credenciales_beta.local.txt",
    ]:
        anterior = raiz / nombre
        if anterior.exists():
            shutil.copy2(anterior, carpeta / anterior.name)
    archivo = carpeta / "credenciales_beta.local.md"
    with Session(motor) as base:
        with base.begin():
            filas = list(
                base.execute(
                    select(Usuario, Persona, Rol)
                    .join(Persona, Usuario.persona_id == Persona.id)
                    .join(Rol, Persona.rol_id == Rol.id)
                )
            )
            if len(filas) != 28 or any(
                not persona.codigo.startswith(("ADM-", "DOC-", "EST-"))
                for _, persona, _ in filas
            ):
                raise RuntimeError(
                    "La actualización está limitada al conjunto de 28 cuentas ficticias iniciales."
                )
            usuarios = [
                usuario.nombre_usuario.replace(".", "") for usuario, _, _ in filas
            ]
            if len(set(usuarios)) != len(usuarios):
                raise RuntimeError(
                    "Los nombres sin puntos coinciden. No se modificaron las cuentas."
                )
            cuentas = []
            for (usuario, persona, rol), nombre in zip(filas, usuarios):
                usuario.nombre_usuario = nombre
                nombre, clave = credenciales_iniciales(persona.nombres, persona.apellidos,
                    lambda candidato: base.scalar(select(Usuario.id).where(
                        Usuario.nombre_usuario == candidato, Usuario.id != usuario.id)) is None)
                usuario.nombre_usuario = nombre
                usuario.clave_hash = generar_hash_clave(clave)
                usuario.debe_cambiar_clave = True
                cuentas.append(
                    {
                        "nombre": f"{persona.nombres} {persona.apellidos}",
                        "usuario": nombre,
                        "clave": clave,
                        "rol": rol.codigo,
                        "permiso": usuario.permiso,
                        "codigo": persona.codigo,
                    }
                )
            base.execute(delete(SesionAcceso))
            for puesto in base.scalars(
                select(PuestoAbierto).where(PuestoAbierto.activo.is_(True))
            ):
                puesto.activo = False
            guardar_listado(cuentas, archivo, respaldo, momento.date())
        shutil.copy2(archivo, raiz / "README_CREDENCIALES.local.md")
        (raiz / "backend/.credenciales_beta.local.txt").write_text(
            "\n".join(f"{cuenta['usuario']}: {cuenta['clave']}" for cuenta in cuentas)
            + "\n",
            encoding="utf-8",
        )
    print(
        f"Actualizados {len(cuentas)} accesos; se conservaron personas, horarios y asistencias."
    )
    print("Credenciales: README_CREDENCIALES.local.md")
    print("Respaldo privado:", respaldo)


if __name__ == "__main__":
    argumentos = ArgumentParser(
        description="Prepara cuentas ficticias iniciales con respaldo obligatorio."
    )
    argumentos.add_argument("--reemplazar-usuarios", action="store_true")
    argumentos.add_argument("--confirmar-base", required=True)
    argumentos.add_argument("--actualizar-accesos", action="store_true")
    opciones = argumentos.parse_args()
    if opciones.actualizar_accesos:
        if opciones.reemplazar_usuarios:
            argumentos.error("No combines actualizar accesos con reemplazar usuarios.")
        actualizar_accesos_iniciales(opciones.confirmar_base)
    else:
        preparar_datos_iniciales(opciones.reemplazar_usuarios, opciones.confirmar_base)
