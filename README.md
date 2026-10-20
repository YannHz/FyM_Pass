# FyM Pass

**0.2.0-beta.3 · beta funcional local**

Sistema web de asistencia del Instituto de Educación Superior Técnica Finney Miller. Administración gestiona personas, horarios, puestos y reportes; estudiantes y personal acceden a su carné y a sus propias asistencias desde el navegador. La misma web puede instalarse como PWA en teléfonos y computadoras.

Los alumnos registran entrada al instituto; docentes y administrativos registran entrada y salida. Se puede mostrar el carné a la cámara del puesto o escanear el QR dinámico con el teléfono. Flutter está descartado. El alojamiento en línea queda para una etapa posterior.

## Tecnologías

| Parte | Tecnologías |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Lucide, QRCode y ZXing |
| Backend | Python, FastAPI, Uvicorn y Pydantic |
| Base de datos | MySQL/MariaDB, SQLAlchemy, PyMySQL y Alembic |
| Archivos | openpyxl para Excel; Pillow conservado en infraestructura histórica de fotos |
| Instalación web | Manifest y service worker para PWA |

## Monolito modular con arquitectura por capas

Una sola API organizada en acceso, asistencia, gestión y diagnóstico. Cada módulo separa rutas HTTP, validación, reglas y consultas. Todos comparten una base de datos.

```text
Navegador / PWA React → Rutas y esquemas → Servicios → Repositorios → MySQL/MariaDB
```

Solo el backend accede a la base. En local, Vite redirige `/api` hacia FastAPI. Los eventos se guardan en UTC y se muestran según la zona de la sede, actualmente Lima. Los detalles están en [arquitectura](docs/arquitectura.md).

## Carpetas

```text
backend/
├── aplicacion/
│   ├── main.py                 Reúne las rutas de FastAPI
│   ├── modulos/
│   │   ├── acceso/             Cuentas y sesiones
│   │   ├── asistencia/         Carnés, QR y marcados
│   │   ├── gestion/            Administración y reportes
│   │   └── diagnostico/        Salud del sistema
│   ├── compartido/             Dependencias, errores y firma QR
│   ├── infraestructura/        Fotos y archivos Excel
│   ├── datos_beta.py           Preparación explícita de datos ficticios
│   ├── models.py               Tablas y entidades
│   ├── database.py             Conexión a la base
│   └── config.py               Configuración privada
├── migraciones/                Versiones del esquema
└── archivos/                   Fotos y respaldos privados, fuera de Git
web/
├── src/
│   ├── App.tsx                 Acceso y recuperación de sesión
│   ├── PanelAdministrativo.tsx  Módulos de administración
│   ├── FormularioGestion.tsx   Formularios y editor de horarios
│   ├── componentesGestion.tsx  Consultas, tablas y diálogos
│   ├── CarneVirtual.tsx        Identificación y escaneo personal
│   ├── PuestoAsistencia.tsx    Pantalla de entrada al instituto
│   ├── servicio.ts            Peticiones y errores de la API
│   └── index.css              Apariencia y adaptación de pantallas
├── public/                     Manifest, iconos y pantalla sin conexión
├── pwa.ts                      Generación del service worker
├── service-worker.js           Plantilla de caché pública
├── package.json                Dependencias y comandos
└── vite.config.ts              Desarrollo y proxy local
docs/                           Guías del sistema
iniciar.sh                      Lanzador local para Linux
```

En los módulos: `rutas.py` recibe peticiones, `esquemas.py` valida entradas, `servicios.py` aplica reglas y `repositorio.py` consulta o guarda. Diagnóstico no necesita un esquema de formulario propio.

Por decisión del usuario, esta versión no incluye archivos de pruebas automatizadas ni configuración de contenedores.

## Preparación local

Requiere Python compatible con las dependencias, Node.js 22, npm y MySQL 8 o MariaDB 10.4 o superior. La instalación actual usa MariaDB de XAMPP. Desde la raíz, en Linux:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

En Windows usa `py -m venv backend/.venv` y `backend\.venv\Scripts\python.exe` en lugar del Python de Linux.

Crea la base `fym_pass` y un usuario dedicado; configura su host, puerto y credenciales en `backend/.env`. Genera `CLAVE_QR` aleatoria de al menos 32 caracteres y consérvala para que los carnés mantengan su validez. No publiques el archivo `.env`.

Después, desde `backend/`:

```sh
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m aplicacion.datos_beta --confirmar-base fym_pass
```

El preparador requiere `mysqldump` o `mariadb-dump`, crea un respaldo privado y rechaza una carga nueva si ya existen personas. No se ejecuta durante el arranque normal. No uses `--reemplazar-usuarios` salvo que quieras descartar expresamente las personas y el historial de esa base local.

## Arranque

En Linux, desde Bash, fish o zsh:

```sh
./iniciar.sh
```

Requiere Bash y Python 3; no ejecutar con `fish iniciar.sh`. MySQL debe estar iniciado. `--sin-navegador` evita abrir el navegador; Ctrl+C cierra los procesos iniciados por el lanzador. Los registros quedan en `.registros/`.

Para iniciar manualmente, desde `backend/`:

```sh
.venv/bin/python -m uvicorn aplicacion.main:aplicacion --host 127.0.0.1 --port 8000
```

En otra terminal, desde `web/`: `npm run dev`.

En Windows (PowerShell), con MySQL de XAMPP iniciado, usar dos terminales:

```powershell
cd D:\dev_\FyM_Pass\backend
.\.venv\Scripts\python.exe -m uvicorn aplicacion.main:aplicacion --host 127.0.0.1 --port 8000
```

```powershell
cd D:\dev_\FyM_Pass\web
npm run dev
```

No ejecutar estos comandos otra vez si esos puertos ya están ocupados por la instalación activa.

Web: `http://127.0.0.1:5173`. API: `http://127.0.0.1:8000/docs`. La opción `./iniciar.sh --red auto` conserva el diagnóstico de la API por red; no habilita HTTPS ni la instalación o cámara del navegador en teléfonos.

## Cuentas locales

28 personas completamente ficticias: 4 administrativos, 6 docentes y 18 estudiantes. Usuarios sin puntos, por ejemplo `mariasalazar`, `rosaquispe`, `luishuaman` y `diegoflores`. Las credenciales completas están en `README_CREDENCIALES.local.md` y `backend/.credenciales_beta.local.txt`, excluidos de Git.

Se mantienen tres carreras ilustrativas y seis grupos. Horarios de lunes a viernes: administración 08–17; docentes 08–13 o 14–19; alumnos entrada a las 08 o 14. Se pueden editar desde el panel. No se generan DNI, fotos reales ni asistencias artificiales; se conservan los registros realizados durante las pruebas.

La herramienta permite actualizar solo los accesos del conjunto ficticio, conservando los datos:

```sh
.venv/bin/python -m aplicacion.datos_beta --actualizar-accesos --confirmar-base fym_pass
```

Esta operación respalda la base, cambia usuarios y claves, revoca sesiones y pausa los puestos abiertos. No borra personas, grupos ni asistencias.

## Compilación e instalación web

`npm --prefix web run build` verifica TypeScript y genera `web/dist/` y el service worker. La PWA instala en un contexto seguro: HTTPS o localhost. En iPhone se añade desde Safari; en Android y PC se usa el menú de instalación del navegador.

La PWA conserva únicamente recursos públicos. No almacena carnés, fotos ni respuestas de la API; no hay sincronización de marcados sin conexión. Ante una caída muestra contingencia y se utiliza el registro manual. Acceso desde teléfono mediante túnel HTTPS y detalles de instalación en la [guía de operación](docs/operacion.md).

## Documentación esencial

- [Arquitectura y base de datos](docs/arquitectura.md): módulos, capas, tablas y seguridad.
- [Operación y pruebas locales](docs/operacion.md): puesto QR, cuentas, PWA, túnel HTTPS y respaldos.
- [Contexto para continuar](CONTEXTO_PROYECTO.md): decisiones vigentes, diseño y pendientes.
- AGENTS.md: convenciones para trabajar en el repositorio.

Las credenciales completas siguen en README_CREDENCIALES.local.md y backend/.credenciales_beta.local.txt, privados y excluidos de Git. Fotos, respaldos y base tampoco viajan con Git; transferirlos por un medio privado al cambiar de equipo.
