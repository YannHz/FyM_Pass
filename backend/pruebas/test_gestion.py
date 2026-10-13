import unittest
from datetime import datetime
from io import BytesIO
from uuid import uuid4
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.orm import Session
from openpyxl import load_workbook
import test_puesto as pruebas_puesto
from aplicacion.models import Marcado, Auditoria, Persona


class PruebasGestion(unittest.TestCase):
    ingresar = pruebas_puesto.PruebasPuesto.ingresar
    setUp = pruebas_puesto.PruebasPuesto.setUp
    tearDown = pruebas_puesto.PruebasPuesto.tearDown

    def guardar(self, ruta, datos):
        return self.cliente.post('/api/gestion/' + ruta, json=datos, headers={'X-Fym-Peticion': '1'})

    def manual(self, persona=3, tipo='entrada', hora='2026-10-11T08:20:00', evento=None):
        with patch('aplicacion.gestion.obtener_hora_utc', return_value=datetime(2026, 10, 11, 23)):
            return self.guardar('manual', {'persona_id': persona, 'tipo': tipo, 'fecha_hora': hora, 'motivo': 'Contingencia de prueba', 'identificador_evento': evento or str(uuid4())})

    def test_manual_idempotente_y_auditado(self):
        evento = str(uuid4())
        primero = self.manual(evento=evento)
        self.assertEqual(primero.status_code, 200, primero.text)
        self.assertEqual(self.manual(evento=evento).json()['id'], primero.json()['id'])
        self.assertEqual(self.manual().status_code, 409)
        self.assertEqual(self.manual(tipo='salida', hora='2026-10-11T17:00:00').status_code, 422)
        with Session(self.motor) as base:
            filas = base.scalars(select(Marcado)).all()
            self.assertEqual(len(filas), 1)
            self.assertEqual(filas[0].ocurrido_en.hour, 13)
            self.assertEqual(filas[0].resultado, 'Tardanza')
            self.assertEqual(base.scalar(select(Auditoria)).usuario_id, 1)

    def test_permisos_operador(self):
        self.ingresar('operador')
        self.assertEqual(self.guardar('carreras', {'nombre': 'Prueba', 'codigo': 'PR'}).status_code, 403)
        self.assertEqual(self.cliente.get('/api/gestion/preplanilla?desde=2026-10-11&hasta=2026-10-11').status_code, 403)
        self.assertEqual(self.cliente.get('/api/gestion/exportar?desde=2026-10-11&hasta=2026-10-11&tipo=preplanilla').status_code, 403)
        self.assertEqual(self.manual().status_code, 200)

    def test_justificacion_conserva_marcado(self):
        self.assertEqual(self.manual().status_code, 200)
        creada = self.guardar('justificaciones', {'persona_id': 3, 'fecha': '2026-10-11', 'tipo': 'tardanza', 'motivo': 'Transporte detenido'})
        self.assertEqual(creada.status_code, 200, creada.text)
        identificador = self.cliente.get('/api/gestion/justificaciones').json()[0]['id']
        self.ingresar('operador')
        datos = {'estado': 'aprobada', 'observacion': 'Revisado en prueba'}
        self.assertEqual(self.guardar(f'justificaciones/{identificador}/resolver', datos).status_code, 403)
        self.ingresar()
        self.assertEqual(self.guardar(f'justificaciones/{identificador}/resolver', datos).status_code, 200)
        filas = self.cliente.get('/api/gestion/diario?desde=2026-10-11&hasta=2026-10-11').json()
        self.assertEqual(next(f for f in filas if f['persona_id'] == 3)['estado'], 'Justificado')
        with Session(self.motor) as base:
            self.assertEqual(base.scalar(select(Marcado)).resultado, 'Tardanza')

    def test_exportacion_y_dia_no_lectivo(self):
        with Session(self.motor) as base:
            base.get(Persona, 3).nombres = '=FORMULA'
            base.commit()
        respuesta = self.cliente.get('/api/gestion/exportar?desde=2026-10-11&hasta=2026-10-11&rol=estudiante')
        self.assertEqual(respuesta.status_code, 200)
        hoja = load_workbook(BytesIO(respuesta.content)).active
        self.assertEqual(hoja.max_row, 2)
        self.assertTrue(any(str(c.value).startswith("'=FORMULA") for c in hoja[2]))
        self.assertEqual(self.guardar('dias-no-lectivos', {'fecha': '2026-10-11', 'motivo': 'Dia no lectivo de prueba'}).status_code, 200)
        filas = self.cliente.get('/api/gestion/diario?desde=2026-10-11&hasta=2026-10-11').json()
        self.assertTrue(all(f['estado'] != 'Falta' for f in filas))

    def test_proteccion_cuenta_propia(self):
        datos = {'id': 1, 'codigo': 'admin', 'nombres': 'Persona', 'apellidos': 'Prueba', 'rol_id': 2, 'activa': False, 'permiso': 'administrador'}
        self.assertEqual(self.guardar('personas', datos).status_code, 422)
        self.assertEqual(self.manual(persona=2, tipo='salida').status_code, 422)
        self.assertEqual(self.manual(hora='2099-10-11T08:00:00').status_code, 422)
