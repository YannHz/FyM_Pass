import unittest
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session
import test_puesto as pruebas_puesto
from aplicacion.models import Persona, ToleranciaRol, ReglaSede


class PruebasIntegracionCapas(unittest.TestCase):
    ingresar = pruebas_puesto.PruebasPuesto.ingresar
    setUp = pruebas_puesto.PruebasPuesto.setUp
    tearDown = pruebas_puesto.PruebasPuesto.tearDown

    def test_foto_se_guarda_en_el_directorio_configurado(self):
        contenido = BytesIO()
        Image.new("RGB", (1024, 800), "blue").save(contenido, format="PNG")
        with TemporaryDirectory() as carpeta:
            with patch("aplicacion.infraestructura.fotos.CARPETA_FOTOS", Path(carpeta)):
                respuesta = self.cliente.post(
                    "/api/gestion/personas/3/foto",
                    files={"archivo": ("foto.png", contenido.getvalue(), "image/png")},
                    headers={"X-Fym-Peticion": "1"},
                )
            self.assertEqual(respuesta.status_code, 200, respuesta.text)
            ruta = respuesta.json()["foto"]
            self.assertTrue(ruta.startswith("/api/fotos/"))
            archivo = Path(carpeta) / ruta.rsplit("/", 1)[1]
            with Image.open(archivo) as foto:
                self.assertEqual(foto.format, "JPEG")
                self.assertLessEqual(max(foto.size), 512)
            with Session(self.motor) as base:
                self.assertEqual(base.get(Persona, 3).foto_ruta, ruta)

    def test_foto_invalida_y_acceso_restringido(self):
        respuesta = self.cliente.post(
            "/api/gestion/personas/3/foto",
            files={"archivo": ("foto.png", b"no es una imagen", "image/png")},
            headers={"X-Fym-Peticion": "1"},
        )
        self.assertEqual(respuesta.status_code, 422)
        self.ingresar("operador")
        respuesta = self.cliente.post(
            "/api/gestion/personas/3/foto",
            files={"archivo": ("foto.png", b"no es una imagen", "image/png")},
            headers={"X-Fym-Peticion": "1"},
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_error_de_regla_revierte_la_transaccion_completa(self):
        datos = {
            "tolerancias": {"1": 25, "999": 10},
            "anticipacion_minutos": 0,
            "limite_ausencia_minutos": 45,
            "observacion_porcentaje": 15,
            "alerta_porcentaje": 30,
        }
        with patch(
            "aplicacion.modulos.gestion.servicios.obtener_hora_utc",
            return_value=datetime(2026, 10, 11, 13),
        ):
            respuesta = self.cliente.post(
                "/api/gestion/reglas", json=datos, headers={"X-Fym-Peticion": "1"}
            )
        self.assertEqual(respuesta.status_code, 422)
        with Session(self.motor) as base:
            tolerancias = base.scalars(select(ToleranciaRol)).all()
            self.assertEqual(len(tolerancias), 2)
            self.assertTrue(
                all(
                    tolerancia.minutos == 10 and tolerancia.vigente_hasta is None
                    for tolerancia in tolerancias
                )
            )
            self.assertIsNone(base.scalar(select(ReglaSede)))

    def test_diagnostico_de_base_y_cache_de_qr(self):
        with self.motor.connect() as conexion:
            conexion.connection.driver_connection.create_function(
                "VERSION", 0, lambda: "10.4.32-MariaDB"
            )
        salud = self.cliente.get("/api/salud/base-datos")
        self.assertEqual(salud.status_code, 200)
        self.assertEqual(salud.json()["motor"], "MariaDB")
        for ruta, encabezados in [
            ("/api/carne", {}),
            ("/api/acceso/actual", {}),
            ("/api/puesto/estado", self.encabezados),
            ("/api/puesto/eventos", self.encabezados),
        ]:
            respuesta = self.cliente.get(ruta, headers=encabezados)
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.headers["cache-control"], "no-store")
