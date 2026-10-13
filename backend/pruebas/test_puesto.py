import unittest
from datetime import datetime, timedelta, date, time
from unittest.mock import patch
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
import test_acceso as pruebas_acceso
from aplicacion.models import (Base, Persona, PuntoAsistencia, PuestoAbierto, Marcado, EventoPuesto,
    Horario, TramoHorario, AsignacionHorario, ToleranciaRol)


class PruebasPuesto(unittest.TestCase):
    ingresar = pruebas_acceso.PruebasAcceso.ingresar
    tearDown = pruebas_acceso.PruebasAcceso.tearDown

    def setUp(self):
        pruebas_acceso.PruebasAcceso.setUp(self)
        with self.motor.connect() as conexion:
            conexion.connection.driver_connection.create_function('CHAR_LENGTH', 1, lambda valor: len(valor) if valor is not None else None)
        Base.metadata.create_all(self.motor)
        with Session(self.motor) as base:
            base.add(PuntoAsistencia(id=1, sede_id=1, nombre='Puesto prueba'))
            base.add(Horario(id=1, sede_id=1, nombre='Horario prueba'))
            base.flush()
            base.add(TramoHorario(horario_id=1, dia_semana=6, hora_entrada=time(8), hora_salida=time(17)))
            for persona in (1, 2, 3):
                base.add(AsignacionHorario(persona_id=persona, horario_id=1, vigente_desde=date(2026, 10, 1)))
            for rol in (1, 2):
                base.add(ToleranciaRol(rol_id=rol, minutos=10, vigente_desde=date(2026, 10, 1)))
            base.commit()
        self.ingresar()
        respuesta = self.cliente.post('/api/asistencia/abrir', json={'camara_puesto_habilitada': True, 'escaneo_movil_habilitado': True}, headers={'X-Fym-Peticion': '1'})
        self.assertEqual(respuesta.status_code, 200)
        self.encabezados = {'X-Fym-Peticion': '1', 'X-Fym-Puesto': respuesta.json()['token_puesto']}

    def carne(self, cuenta='estudiante'):
        self.ingresar(cuenta)
        respuesta = self.cliente.get('/api/carne')
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.json()['qr']

    def leer(self, contenido, identificador=None):
        return self.cliente.post('/api/puesto/leer', json={'contenido': contenido, 'identificador_evento': identificador or str(uuid4())}, headers=self.encabezados)

    def test_carne_registro_y_confirmacion(self):
        carne = self.carne()
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=datetime(2026, 10, 11, 13, 5)):
            respuesta = self.leer(carne)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertTrue(datos['aceptado'])
        self.assertEqual(datos['tipo'], 'entrada')
        self.assertEqual(datos['resultado'], 'Puntual')
        self.assertEqual(datos['persona']['rol'], 'Estudiante')
        self.assertIn('foto', datos['persona'])
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=datetime(2026, 10, 11, 13, 5, 1)):
            eventos = self.cliente.get('/api/puesto/eventos', headers=self.encabezados).json()
        self.assertEqual(len(eventos), 1)

    def test_estudiante_una_entrada_e_idempotencia(self):
        carne = self.carne()
        evento = str(uuid4())
        ahora = datetime(2026, 10, 11, 13, 5)
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=ahora):
            self.leer(carne, evento)
            self.assertTrue(self.leer(carne, evento).json()['repetido'])
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=ahora + timedelta(seconds=2)):
            self.assertTrue(self.leer(carne).json()['repetido'])
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=ahora + timedelta(seconds=11)):
            self.assertFalse(self.leer(carne).json()['aceptado'])
        with Session(self.motor) as base:
            self.assertEqual(len(base.scalars(select(Marcado)).all()), 1)

    def test_entrada_salida_personal(self):
        carne = self.carne('operador')
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=datetime(2026, 10, 11, 13, 15)):
            entrada = self.leer(carne).json()
        self.assertEqual(entrada['resultado'], 'Tardanza')
        with patch('aplicacion.asistencia.obtener_hora_utc', return_value=datetime(2026, 10, 11, 22)):
            salida = self.leer(carne).json()
        self.assertEqual(salida['tipo'], 'salida')
        self.assertTrue(salida['aceptado'])

    def test_qr_movil_y_vencimiento(self):
        qr = self.cliente.get('/api/puesto/estado', headers=self.encabezados).json()['qr']
        self.ingresar('estudiante')
        datos = {'contenido': qr, 'identificador_evento': str(uuid4())}
        respuesta = self.cliente.post('/api/carne/marcar', json=datos, headers={'X-Fym-Peticion': '1'})
        self.assertTrue(respuesta.json()['aceptado'])
        with patch('aplicacion.asistencia.time.time', return_value=(int(qr.split(':')[3]) + 1) * 30):
            self.assertEqual(self.cliente.post('/api/carne/marcar', json=datos, headers={'X-Fym-Peticion': '1'}).status_code, 409)

    def test_firma_alterada_rechazada(self):
        qr = self.carne()
        respuesta = self.leer(qr[:-1] + ('0' if qr[-1] != '0' else '1'))
        self.assertFalse(respuesta.json()['aceptado'])
        self.assertIsNone(respuesta.json()['persona'])
        with Session(self.motor) as base:
            self.assertEqual(len(base.scalars(select(Marcado)).all()), 0)

    def test_sede_y_persona_inactiva(self):
        carne = self.carne()
        with Session(self.motor) as base:
            base.get(Persona, 3).activa = False
            base.commit()
        self.assertFalse(self.leer(carne).json()['aceptado'])

    def test_modalidad_desactivada_y_pausa(self):
        carne = self.carne()
        with Session(self.motor) as base:
            base.get(PuntoAsistencia, 1).camara_puesto_habilitada = False
            base.commit()
        self.assertEqual(self.leer(carne).status_code, 409)
        self.ingresar()
        self.assertEqual(self.cliente.post('/api/asistencia/pausar', headers={'X-Fym-Peticion': '1'}).status_code, 200)
        self.assertEqual(self.cliente.get('/api/puesto/estado', headers=self.encabezados).status_code, 409)

    def test_personal_no_abre_puesto(self):
        self.ingresar('estudiante')
        self.assertEqual(self.cliente.post('/api/asistencia/abrir', json={'camara_puesto_habilitada': True, 'escaneo_movil_habilitado': True}, headers={'X-Fym-Peticion': '1'}).status_code, 403)
        self.assertEqual(self.cliente.get('/api/puesto/eventos').status_code, 401)


if __name__ == '__main__':
    unittest.main()
