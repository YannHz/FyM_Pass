# FyM Pass

El usuario inicial se genera con la inicial del primer nombre, el primer apellido y `fym`, en minúsculas y sin tildes. Si coincide con otra cuenta, se añaden las iniciales de los apellidos restantes antes de `fym`. Una coincidencia adicional requiere revisar los datos con administración. La contraseña inicial combina el primer nombre y las iniciales de los apellidos.

En el primer ingreso es obligatorio establecer una contraseña distinta, de al menos 8 caracteres, y escribirla de nuevo para confirmarla. Hasta completar ese paso, la API bloquea el acceso a los módulos. La migración 0006 incorpora el indicador de cambio pendiente; las nuevas cuentas lo activan automáticamente.

## Resumen

FyM Pass es un sistema web para registrar y administrar la asistencia de ingreso al Instituto de Educación Superior Tecnológico Finney y Miller. Permite trabajar con carnets y códigos QR, consultar la jornada diaria, organizar personas y horarios, gestionar justificaciones y generar reportes en Excel.

La aplicación incluye un panel administrativo y un espacio personal para docentes y personal administrativo. Puede utilizarse desde el navegador o instalarse como una aplicación web progresiva (PWA).

## Stack de desarrollo

| Área | Tecnologías |
| --- | --- |
| Frontend | React 19, TypeScript, Vite 6 y Tailwind CSS 4 |
| Interfaz | Lucide React, QRCode y ZXing |
| Backend | Python, FastAPI, Uvicorn y Pydantic |
| Persistencia | MySQL o MariaDB, SQLAlchemy, PyMySQL y Alembic |
| Reportes | openpyxl |
| Aplicación instalable | Web App Manifest y service worker |

## Arquitectura

El proyecto usa un monolito modular con arquitectura por capas. El frontend consume una única API y el backend agrupa los módulos de acceso, asistencia, gestión y diagnóstico. Todos los módulos comparten la misma base de datos.

```text
Navegador o PWA
       │
       ▼
Frontend React
       │ HTTP / JSON
       ▼
Rutas y esquemas FastAPI
       │
       ▼
Servicios y reglas de negocio
       │
       ▼
Repositorios y modelos SQLAlchemy
       │
       ▼
MySQL o MariaDB
```

- Las rutas reciben las peticiones, verifican permisos y preparan las respuestas.
- Los esquemas validan los datos de entrada y salida.
- Los servicios coordinan las reglas del sistema y las transacciones.
- Los repositorios concentran las consultas y operaciones de persistencia.
- Alembic mantiene la evolución del esquema de la base de datos.
- La generación de reportes Excel se encuentra en la capa de infraestructura.

## Estructura del backend

```text
backend/
├── aplicacion/
│   ├── main.py                 punto de entrada de la API
│   ├── config.py               configuración del entorno
│   ├── database.py             conexión y sesión de base de datos
│   ├── models.py               modelos ORM
│   ├── seguridad.py            autenticación, sesiones y contraseñas
│   ├── datos_iniciales.py      carga opcional de datos iniciales
│   ├── compartido/             utilidades comunes y dependencias
│   ├── infraestructura/        generación de reportes Excel
│   └── modulos/
│       ├── acceso/             cuentas y sesiones
│       ├── asistencia/         carnets, puestos y marcados
│       ├── gestion/            personas, horarios y reportes
│       └── diagnostico/        estado de la aplicación y la base
├── migraciones/                revisiones de Alembic
├── .env.example                variables de entorno de referencia
├── alembic.ini                 configuración de migraciones
├── requirements.txt            rangos de dependencias
└── requirements.lock           dependencias fijadas
```

Los módulos aplican la misma separación cuando corresponde: `rutas.py` expone la API, `esquemas.py` valida los datos, `servicios.py` contiene las reglas y `repositorio.py` accede a la base.

## Estructura del frontend

```text
web/
├── src/
│   ├── main.tsx                inicio de React
│   ├── App.tsx                 sesión y navegación principal
│   ├── PanelAdministrativo.tsx panel de administración
│   ├── EspacioPersonal.tsx     carnet y asistencia personal
│   ├── PuestoAsistencia.tsx    pantalla del puesto de ingreso
│   ├── servicio.ts             comunicación con la API
│   ├── componentesGestion.tsx  componentes administrativos comunes
│   ├── controles.css           estilos de controles compartidos
│   └── index.css               tema y estilos generales
├── public/                     iconos, manifest y página sin conexión
├── pwa.ts                      preparación de la PWA
├── service-worker.js           caché de recursos públicos
├── index.html                  documento principal
├── package.json                scripts y dependencias
├── tsconfig.json               configuración de TypeScript
└── vite.config.ts              compilación, servidor y proxy local
```

Las pantallas y sus estilos se organizan por función dentro de `web/src`. Los controles reutilizables para fechas, horas, filtros, tema y menús también se encuentran en esa carpeta.

## Requisitos para ejecutarlo en local

- Python 3 compatible con `backend/requirements.lock`.
- Node.js 22 o superior con npm.
- MySQL 8 o MariaDB 10.4 o superior.
- Bash y Python 3 para utilizar `iniciar.sh` en Linux o macOS.
- Cloudflared en el `PATH` si se necesita acceso HTTPS desde un teléfono.
- Una base de datos llamada `fym_pass` y un usuario con permisos sobre ella.

## Guía para ejecutarlo en local

### 1. Instalar las dependencias

En Linux o macOS, desde la raíz del proyecto:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

En Windows, desde PowerShell:

```powershell
py -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
npm --prefix web ci
Copy-Item backend/.env.example backend/.env
```

### 2. Configurar la base de datos

Inicia MySQL o MariaDB, crea la base `fym_pass` y completa `backend/.env`:

```dotenv
BD_HOST=127.0.0.1
BD_PUERTO=3306
BD_USUARIO=fym_pass
BD_CLAVE=
BD_NOMBRE=fym_pass

CLAVE_QR=
COOKIE_SEGURA=false
PROXY_CONFIABLE=false
```

`CLAVE_QR` debe contener una clave aleatoria de al menos 32 caracteres. Debe conservarse para que los carnets emitidos sigan siendo válidos.

- `COOKIE_SEGURA=false` entrega la cookie sin el atributo `Secure`; útil en desarrollo local. Antes de servir en producción por HTTPS se define `COOKIE_SEGURA=true`, con lo que la API además envía el encabezado `Strict-Transport-Security` y registra un aviso si se arranca sin esa configuración.
- `PROXY_CONFIABLE=false` limita los intentos de acceso por la IP directa del cliente. Colócalo en `true` solo cuando la API corra detrás de un proxy que entrega la IP real en `X-Forwarded-For` (por ejemplo nginx); si no, alguien podría falsear esa cabecera para burlar el límite.

Respuestas de la API y restauración:

- Cambiar la contraseña de una persona por Personas y carnets cierra de inmediato todas las sesiones abiertas de esa cuenta; quien la tuviera abierta debe iniciar sesión de nuevo.
- La ruta pública `/api/salud` solo indica vida de la API; el estado de la base de datos quedó en `/api/salud/base-datos`, que ahora exige sesión de encargado.
- La API agrega `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy` a todas las respuestas.

### 3. Aplicar las migraciones

En Linux o macOS:

```sh
cd backend
.venv/bin/python -m alembic upgrade head
cd ..
```

En Windows:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m alembic upgrade head
Set-Location ..
```

En una instalación vacía se pueden cargar los datos iniciales desde `backend`:

```sh
.venv/bin/python -m aplicacion.datos_iniciales --confirmar-base fym_pass
```

En Windows, reemplaza `.venv/bin/python` por `.\.venv\Scripts\python.exe`.

### 4. Iniciar la aplicación

En Linux o macOS, con MySQL activo:

```sh
./iniciar.sh
```

El script comprueba la configuración, las migraciones y las versiones; después compila la web e inicia la API en `127.0.0.1:8000` y la web en `127.0.0.1:4173`. Desde fish debe ejecutarse como `./iniciar.sh`, porque el propio archivo utiliza Bash.

Para trabajar con recarga automática y sin PWA:

```sh
./iniciar.sh --desarrollo
```

En Windows, inicia la API desde una terminal PowerShell:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -B -m uvicorn aplicacion.main:aplicacion --host 127.0.0.1 --port 8000
```

Luego compila y sirve la web desde otra terminal situada en la raíz:

```powershell
npm --prefix web run build
node .\web\node_modules\vite\bin\vite.js preview --host 127.0.0.1 --port 4173 --strictPort
```

La aplicación queda disponible en `http://127.0.0.1:4173` y la documentación de la API en `http://127.0.0.1:8000/docs`.

### 5. Abrir un túnel HTTPS con Cloudflare

Con MySQL, la API y la web activos, ejecuta en otra terminal:

```sh
cloudflared tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

Si Cloudflared está instalado en su ubicación habitual de Windows pero no está en el `PATH`:

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

Cloudflare mostrará una URL HTTPS temporal. Ábrela en el teléfono para utilizar la cámara o instalar la PWA. La terminal del túnel y los servicios locales deben permanecer abiertos durante el uso.

### 6. Actualización de la aplicación instalada

Cuando se publica una versión nueva, las pestañas y equipos instalados con la PWA muestran un mensaje "FyM Pass se actualizó" con el botón "Recargar ahora". El contenido sigue usándose hasta que alguien acepte recargar, así que ninguna operación en curso se interrumpe a mitad de guardado.
