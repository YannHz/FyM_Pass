import ast
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from aplicacion.main import aplicacion
from aplicacion.compartido.errores import ErrorAplicacion, FalloPersistencia
from aplicacion.modulos.gestion.esquemas import DatosHorario
from aplicacion.modulos.gestion.servicios import guardar_horario
from aplicacion.modulos.diagnostico.servicios import consultar_base_datos


class PruebasCapas(unittest.TestCase):
    def test_contrato_http_conservado(self):
        ruta = Path(__file__).parent / "contratos/openapi.json"
        esperado = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertEqual(aplicacion.openapi(), esperado)

    def test_servicios_y_esquemas_no_importan_http_ni_consultas(self):
        raiz = Path(__file__).resolve().parents[1] / "aplicacion/modulos"
        for patron in ["*/servicios.py", "*/esquemas.py"]:
            for ruta in raiz.glob(patron):
                with self.subTest(archivo=str(ruta.relative_to(raiz))):
                    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
                    for nodo in ast.walk(arbol):
                        if isinstance(nodo, ast.ImportFrom):
                            self.assertFalse(
                                (nodo.module or "").startswith(
                                    ("fastapi", "starlette", "sqlalchemy")
                                )
                            )
                        if isinstance(nodo, ast.Import):
                            self.assertTrue(
                                all(
                                    not alias.name.startswith(
                                        ("fastapi", "starlette", "sqlalchemy")
                                    )
                                    for alias in nodo.names
                                )
                            )
                        if isinstance(nodo, ast.Call) and isinstance(
                            nodo.func, ast.Name
                        ):
                            self.assertNotIn(
                                nodo.func.id,
                                [
                                    "select",
                                    "update",
                                    "delete",
                                    "Session",
                                    "create_engine",
                                    "Depends",
                                ],
                            )
                        if isinstance(nodo, ast.Attribute):
                            self.assertNotEqual(nodo.attr, "_base")

    def test_repositorios_no_importan_presentacion_ni_servicios(self):
        raiz = Path(__file__).resolve().parents[1] / "aplicacion/modulos"
        for ruta in raiz.glob("*/repositorio.py"):
            for nodo in ast.walk(ast.parse(ruta.read_text(encoding="utf-8"))):
                if isinstance(nodo, ast.ImportFrom):
                    self.assertFalse(
                        (nodo.module or "").startswith(("fastapi", "starlette"))
                    )
                    self.assertNotIn("servicios", (nodo.module or "").split("."))
                    self.assertNotIn("rutas", (nodo.module or "").split("."))

    def test_regla_de_horario_se_valida_sin_http_ni_base(self):
        datos = DatosHorario(
            nombre="Prueba",
            tramos=[{"dia_semana": 0, "hora_entrada": "17:00", "hora_salida": "08:00"}],
        )
        with self.assertRaises(ErrorAplicacion) as capturado:
            guardar_horario(datos, SimpleNamespace(), None)
        self.assertEqual(capturado.exception.codigo, 422)
        self.assertEqual(
            capturado.exception.mensaje, "La salida debe ser posterior a la entrada."
        )

    def test_salud_traduce_fallo_de_persistencia_sin_http(self):
        class RepositorioCaido:
            def version_base(self):
                raise FalloPersistencia()

        self.assertEqual(
            consultar_base_datos(RepositorioCaido())["estado"], "sin conexion"
        )
