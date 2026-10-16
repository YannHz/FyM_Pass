import unittest
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4
from io import BytesIO
from sqlalchemy import select
from sqlalchemy.orm import Session
from openpyxl import load_workbook
import test_puesto as pruebas_puesto
from aplicacion.models import Marcado, Auditoria
from aplicacion.modulos.diagnostico.servicios import direccion_movil


class PruebasJornada(unittest.TestCase):
    ingresar = pruebas_puesto.PruebasPuesto.ingresar
    setUp = pruebas_puesto.PruebasPuesto.setUp
    tearDown = pruebas_puesto.PruebasPuesto.tearDown
    carne = pruebas_puesto.PruebasPuesto.carne
    leer = pruebas_puesto.PruebasPuesto.leer

    def leer_en(self, qr, hora, evento=None):
        with patch('aplicacion.modulos.asistencia.servicios.obtener_hora_utc', return_value=hora):
            return self.leer(qr, evento)

    def test_recorrido_completo_de_jornada(self):
        estudiante = self.carne()
        evento = str(uuid4())
        primera = self.leer_en(estudiante, datetime(2026, 10, 11, 13, 5), evento)
        self.assertEqual(primera.status_code, 200)
        self.assertEqual(primera.json()['resultado'], 'Puntual')
        repetida = self.leer_en(estudiante, datetime(2026, 10, 11, 13, 5), evento)
        self.assertTrue(repetida.json()['repetido'])
        rechazada = self.leer_en(estudiante, datetime(2026, 10, 11, 13, 6))
        self.assertFalse(rechazada.json()['aceptado'])
        personal = self.carne('operador')
        entrada = self.leer_en(personal, datetime(2026, 10, 11, 13, 20))
        self.assertEqual(entrada.json()['resultado'], 'Tardanza')
        cercana = self.leer_en(personal, datetime(2026, 10, 11, 13, 20, 2))
        self.assertTrue(cercana.json()['repetido'])
        salida = self.leer_en(personal, datetime(2026, 10, 11, 22))
        self.assertTrue(salida.json()['aceptado'])
        self.assertEqual(salida.json()['tipo'], 'salida')
        self.ingresar()
        encabezados = {'X-Fym-Peticion': '1'}
        self.assertEqual(self.cliente.post('/api/asistencia/pausar', headers=encabezados).status_code, 200)
        self.assertEqual(self.leer(estudiante).status_code, 409)
        manual = {'persona_id': 1, 'tipo': 'entrada', 'fecha_hora': '2026-10-11T08:07:00', 'motivo': 'Contingencia durante la jornada', 'identificador_evento': str(uuid4())}
        with patch('aplicacion.modulos.gestion.servicios.obtener_hora_utc', return_value=datetime(2026, 10, 11, 23)):
            guardado = self.cliente.post('/api/gestion/manual', json=manual, headers=encabezados)
            self.assertEqual(guardado.status_code, 200, guardado.text)
            self.assertEqual(self.cliente.post('/api/gestion/manual', json=manual, headers=encabezados).json()['id'], guardado.json()['id'])
        diario = self.cliente.get('/api/gestion/diario?desde=2026-10-11&hasta=2026-10-11').json()
        self.assertEqual(next(fila for fila in diario if fila['persona_id'] == 3)['estado'], 'Puntual')
        self.assertEqual(next(fila for fila in diario if fila['persona_id'] == 2)['estado'], 'Tardanza')
        reporte = self.cliente.get('/api/gestion/exportar?desde=2026-10-11&hasta=2026-10-11')
        self.assertEqual(reporte.status_code, 200)
        self.assertEqual(load_workbook(BytesIO(reporte.content)).active.max_row, 4)
        with Session(self.motor) as base:
            marcados = base.scalars(select(Marcado)).all()
            self.assertEqual(len(marcados), 4)
            carga = next(marcado for marcado in marcados if marcado.modalidad == 'manual')
            self.assertEqual(carga.ocurrido_en, datetime(2026, 10, 11, 13, 7))
            self.assertEqual(carga.registrado_por_id, 1)
            self.assertEqual(base.scalar(select(Auditoria).where(Auditoria.accion == 'registro_manual')).entidad_id, carga.id)

    def test_diagnostico_protegido_y_direcciones(self):
        self.assertEqual(self.cliente.get('/api/diagnostico/conexion').status_code, 200)
        self.ingresar('estudiante')
        self.assertEqual(self.cliente.get('/api/diagnostico/conexion').status_code, 403)
        self.cliente.post('/api/acceso/cerrar', headers={'X-Fym-Peticion': '1'})
        self.assertEqual(self.cliente.get('/api/diagnostico/conexion').status_code, 401)
        self.assertEqual(direccion_movil(('192.168.1.10', 8000)), 'http://192.168.1.10:8000')
        for host in ['127.0.0.1', '0.0.0.0', '169.254.1.2', '8.8.8.8', 'testserver']:
            self.assertIsNone(direccion_movil((host, 8000)))
