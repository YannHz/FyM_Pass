# FyM Pass

FyM Pass es el sistema web de control de asistencia de ingreso del Instituto de Educación Superior Tecnológico Finney y Miller. La versión 1.0.0 funciona en navegadores de escritorio y móviles y puede instalarse como aplicación web progresiva (PWA).

Registra una entrada y una salida por jornada para docentes y personal administrativo de la sede principal. Admite un puesto con QR dinámico y lectura del carné por cámara. Incluye consulta de asistencias, horarios laborales, justificaciones, registro manual auditado, reportes y preplanilla estimada. El ingreso al instituto se mantiene separado de la asistencia a clases.

## Arquitectura

La aplicación sigue un monolito modular con tres partes:

```text
Navegador / PWA → API FastAPI → MySQL o MariaDB
```

El frontend está construido con React, TypeScript y Vite. El backend usa FastAPI, SQLAlchemy y PyMySQL. Alembic administra las migraciones de la base de datos. Solo la API accede a la base; las reglas de permisos y las operaciones sensibles se aplican en el servidor.

La PWA permite instalar la interfaz y conservar recursos públicos para la pantalla sin conexión. El registro de asistencia requiere conexión con la API. Los códigos QR se validan en el backend.

## Estructura del backend

```text
backend/
  aplicacion/
    main.py                 entrada de la API
    config.py               configuración de la aplicación
    database.py             conexión con la base de datos
    models.py               modelos de datos
    seguridad.py            funciones de seguridad
    compartido/             dependencias y lógica compartida
    infraestructura/        generación de reportes
    modulos/
      acceso/               autenticación, sesiones y permisos
      asistencia/           puestos, carnés y marcados
      gestion/              personas, horarios y administración
      diagnostico/          estado del servicio
  migraciones/versiones/    migraciones Alembic
  requirements.txt          dependencias Python
  requirements.lock         versiones fijadas
  .env.example              nombres de variables sin credenciales
```

Las migraciones y los modelos son la definición publicable del esquema. Los datos operativos y los respaldos no forman parte del repositorio.

## Estructura del frontend

```text
web/
  src/
    App.tsx                 entrada de la interfaz
    main.tsx                montaje de React
    servicio.ts             comunicación con la API
    *.tsx y *.css           pantallas, componentes y estilos
  public/                   iconos, manifiesto y página sin conexión
  pwa.ts                    configuración de la PWA
  service-worker.js         caché de recursos públicos
  vite.config.ts            configuración de Vite
  package.json              dependencias y comandos del frontend
```

La interfaz ofrece vistas distintas según el permiso de cada cuenta: personal, operación de asistencia o administración.

## Requisitos de uso

- Un navegador moderno en computadora o teléfono con acceso a la aplicación.
- Conexión a Internet para iniciar sesión, consultar datos y registrar asistencia.
- Acceso HTTPS para instalar la PWA y utilizar la cámara desde el navegador.
- Permiso de cámara en el dispositivo que lea códigos QR.
- Una cuenta habilitada por la administración con el permiso correspondiente.
- El servicio de API y la base MySQL/MariaDB disponibles para las funciones de asistencia.
