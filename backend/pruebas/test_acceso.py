import unittest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from aplicacion.main import aplicacion
from aplicacion.acceso import obtener_base_datos, intentos
from aplicacion.models import Base, Persona, Rol, Sede, Usuario, SesionAcceso, obtener_hora_utc
from aplicacion.seguridad import generar_hash_clave, verificar_clave


class PruebasAcceso(unittest.TestCase):
    def setUp(self):
        self.motor = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.motor, tables=[Sede.__table__, Rol.__table__, Persona.__table__, Usuario.__table__, SesionAcceso.__table__])
        with Session(self.motor) as base:
            base.add(Sede(id=1, codigo='prueba', nombre='Sede prueba'))
            base.add_all([Rol(id=1, codigo='estudiante', nombre='Estudiante', requiere_salida=False), Rol(id=2, codigo='administrativo', nombre='Administrativo', requiere_salida=True)])
            base.flush()
            for identificador, nombre, permiso, rol in [(1, 'admin', 'administrador', 2), (2, 'operador', 'operador', 2), (3, 'estudiante', 'personal', 1)]:
                base.add(Persona(id=identificador, codigo=nombre, nombres='Persona', apellidos='Prueba', sede_id=1, rol_id=rol))
                base.flush()
                base.add(Usuario(id=identificador, persona_id=identificador, nombre_usuario=nombre, clave_hash=generar_hash_clave('clave de prueba'), permiso=permiso))
            base.commit()
        def obtener_base_prueba():
            with Session(self.motor) as base:
                yield base
        aplicacion.dependency_overrides[obtener_base_datos] = obtener_base_prueba
        intentos.clear()
        self.cliente = TestClient(aplicacion)

    def tearDown(self):
        self.cliente.close()
        aplicacion.dependency_overrides.clear()
        self.motor.dispose()

    def ingresar(self, usuario='admin', clave='clave de prueba'):
        return self.cliente.post('/api/acceso/iniciar', json={'usuario': usuario, 'clave': clave}, headers={'X-Fym-Peticion': '1'})

    def test_acceso_y_destinos(self):
        for cuenta, destino in [('admin', '/administracion'), ('operador', '/operacion'), ('estudiante', '/mi-acceso')]:
            with self.subTest(cuenta=cuenta):
                respuesta = self.ingresar(cuenta)
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(respuesta.json()['destino'], destino)
                self.assertIn('HttpOnly', respuesta.headers['set-cookie'])
                self.assertIn('SameSite=strict', respuesta.headers['set-cookie'])
                self.assertNotIn('clave_hash', respuesta.text)
                self.assertEqual(self.cliente.get('/api/acceso/actual').status_code, 200)

    def test_credenciales_incorrectas(self):
        for cuenta in ['admin', 'inexistente']:
            respuesta = self.ingresar(cuenta, 'incorrecta')
            self.assertEqual(respuesta.status_code, 401)
            self.assertEqual(respuesta.json()['detail'], 'Usuario o contraseña incorrectos.')

    def test_panel_protegido(self):
        self.assertEqual(self.cliente.get('/api/administracion/resumen').status_code, 401)
        self.ingresar('estudiante')
        self.assertEqual(self.cliente.get('/api/administracion/resumen').status_code, 403)
        self.ingresar('operador')
        self.assertEqual(self.cliente.get('/api/administracion/resumen').status_code, 200)

    def test_cierre_revoca_token(self):
        self.ingresar()
        token = self.cliente.cookies.get('fym_sesion')
        self.assertEqual(self.cliente.post('/api/acceso/cerrar', headers={'X-Fym-Peticion': '1'}).status_code, 200)
        self.assertEqual(self.cliente.get('/api/acceso/actual', headers={'Cookie': f'fym_sesion={token}'}).status_code, 401)

    def test_cuenta_inactiva(self):
        self.ingresar()
        with Session(self.motor) as base:
            base.get(Usuario, 1).activo = False
            base.commit()
        self.assertEqual(self.cliente.get('/api/acceso/actual').status_code, 401)
        self.assertEqual(self.ingresar().status_code, 401)

    def test_sesion_expirada(self):
        self.ingresar()
        with Session(self.motor) as base:
            sesion = base.scalar(select(SesionAcceso))
            sesion.vence_en = obtener_hora_utc() - timedelta(seconds=1)
            base.commit()
        self.assertEqual(self.cliente.get('/api/acceso/actual').status_code, 401)

    def test_peticion_sin_encabezado(self):
        self.assertEqual(self.cliente.post('/api/acceso/iniciar', json={'usuario': 'admin', 'clave': 'clave de prueba'}).status_code, 403)
        self.assertEqual(self.cliente.post('/api/acceso/cerrar').status_code, 403)

    def test_limite_intentos(self):
        for _ in range(10):
            self.assertEqual(self.ingresar('inexistente', 'incorrecta').status_code, 401)
        self.assertEqual(self.ingresar().status_code, 429)

    def test_hash_sesion_y_clave(self):
        self.ingresar()
        with Session(self.motor) as base:
            sesion = base.scalar(select(SesionAcceso))
            self.assertNotEqual(sesion.token_hash, self.cliente.cookies.get('fym_sesion'))
            usuario = base.get(Usuario, 1)
            self.assertNotEqual(usuario.clave_hash, 'clave de prueba')
            self.assertTrue(verificar_clave('clave de prueba', usuario.clave_hash))


if __name__ == '__main__':
    unittest.main()
