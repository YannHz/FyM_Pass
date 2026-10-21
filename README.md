# FyM Pass

**Versión 1.0.0 · primera versión funcional · ejecución local**

Sistema web de asistencia del Instituto de Educación Superior Técnica Finney Miller. Permite registrar el ingreso al instituto, administrar personas y horarios, justificar tardanzas e inasistencias y consultar reportes. Estudiantes, docentes y administrativos acceden a su carnet y a sus asistencias desde el navegador. La web puede instalarse como PWA en Android, iPhone y computadoras.

## Funciones

- **Asistencia:** estudiantes registran entrada; docentes y administrativos, entrada y salida. Administración puede habilitar el QR dinámico para escaneo desde el teléfono, la lectura del carnet con cámara o ambas modalidades.
- **Jornada diaria:** muestra solo personas con marcados, se actualiza al confirmar cada registro y comienza visualmente vacía al cambiar el día. El historial se conserva.
- **Personas y carnets:** búsqueda por nombre, ID, documento o usuario; filtros por rol, estado y cuenta; expediente con calendario, carnet y horario. Todas las personas se identifican mediante iniciales, sin carga de fotografías.
- **Carreras y horarios:** carrera → ciclo y turno → alumnos registrados o nuevos → confirmación del horario y fecha de inicio. No se usan secciones. Docentes y administrativos tienen horarios laborales separados con entrada y salida.
- **Reportes:** periodos rápidos o intervalos de hasta 62 días, filtros, resumen y expediente del periodo. Excel con consolidado, cuadrícula mensual por rol y detalle diario con horas de Lima. Exporta todos los resultados filtrados.
- **Preplanilla docente:** revisión de minutos y días de tardanza, faltas y salidas pendientes. Los importes son estimaciones secundarias; no aplica descuentos ni determina pagos.
- **Justificaciones:** bandeja de tardanzas y faltas al superar el límite configurado, búsqueda por nombre o ID y formulario por incidencia. Operadores registran solicitudes; administradores aprueban u observan. Se evitan duplicados pendientes o aprobados.
- **Reglas:** tolerancia por rol, anticipación de ingreso, límite para evaluar ausencia, umbrales de seguimiento y calendario de días no lectivos.
- **Espacio personal:** carnet y calendario de asistencias con navegación por mes, selección de fecha y consulta de registros propios.

El registro corresponde al ingreso al instituto, no a la asistencia a clases. Los estados de seguimiento no generan sanciones académicas. La confirmación permanece tres segundos: verde para puntualidad, ámbar para tardanza, azul para otros marcados aceptados o repetidos y rojo para rechazo.

## Tecnologías

| Parte | Tecnologías |
| --- | --- |
| Frontend | React 19, TypeScript, Vite 6, Tailwind CSS, Lucide, QRCode y ZXing |
| Backend | Python, FastAPI, Uvicorn y Pydantic |
| Datos | MySQL/MariaDB, SQLAlchemy, PyMySQL y Alembic |
| Reportes | openpyxl |
| Instalación web | Manifest y service worker para PWA |

## Monolito modular con arquitectura por capas

Una sola API agrupa acceso, asistencia, gestión y diagnóstico. Cada módulo separa la entrada HTTP, las reglas del sistema y el acceso a los datos. Todos comparten una base MySQL/MariaDB.

```text
Navegador / PWA React
          ↓
Rutas HTTP y esquemas de validación
          ↓
Servicios: reglas y operaciones
          ↓
Repositorios: consultas y persistencia
          ↓
MySQL / MariaDB
```

Solo el backend accede a la base. Las rutas resuelven permisos y parámetros; los esquemas validan entradas; los servicios coordinan operaciones y transacciones; los repositorios ejecutan SQL y bloqueos. Excel se genera en infraestructura. Los modelos ORM y utilidades comunes se comparten.

Se usa esta arquitectura porque permite organizar las funciones sin mantener varios servidores independientes. Sigue siendo un único despliegue; no es una arquitectura de microservicios.

## Estructura de carpetas

```text
backend/
├── aplicacion/
│   ├── main.py                 Compone la API y sus manejadores de errores
│   ├── version.py              Versión de la API
│   ├── config.py               Configuración desde el entorno
│   ├── database.py             Conexión a la base
│   ├── models.py               Tablas y entidades
│   ├── seguridad.py            Contraseñas y tokens
│   ├── datos_iniciales.py      Preparación opcional de cuentas ficticias
│   ├── compartido/             Permisos, errores, firma QR y avisos
│   ├── infraestructura/        Generación de archivos Excel
│   └── modulos/
│       ├── acceso/             Cuentas y sesiones
│       ├── asistencia/         Carnets, puestos QR y marcados
│       ├── gestion/            Personas, horarios, incidencias y reportes
│       └── diagnostico/        Estado del servidor y base
├── migraciones/                Cambios del esquema y datos con Alembic
├── archivos/                   Archivos y respaldos privados, fuera de Git
├── .env.example                Ejemplo de configuración
└── requirements.lock           Dependencias fijadas
web/
├── src/
│   ├── App.tsx                 Acceso y recuperación de sesión
│   ├── PanelAdministrativo.tsx  Composición del panel administrativo
│   ├── PersonasCarnets.tsx     Directorio institucional
│   ├── CarrerasHorarios.tsx    Grupos y horarios laborales
│   ├── ReportesAsistencia.tsx  Consulta y exportación
│   ├── PreplanillaDocente.tsx  Tardanzas de docentes
│   ├── Justificaciones.tsx     Incidencias y revisión
│   ├── ToleranciasReglas.tsx   Reglas y días no lectivos
│   ├── FormularioGestion.tsx   Formularios compartidos
│   ├── componentesGestion.tsx  Consultas, tablas y diálogos
│   ├── CarneVirtual.tsx       Identificación y escaneo personal
│   ├── MisAsistencias.tsx     Calendario personal
│   ├── PuestoAsistencia.tsx   Pantalla de entrada al instituto
│   ├── servicio.ts            Peticiones y errores de la API
│   └── index.css              Tema y estilos generales
├── public/                     Iconos, manifest y pantalla sin conexión
├── pwa.ts                      Generación del service worker
├── service-worker.js           Plantilla de caché pública
├── package.json                Dependencias y versión del frontend
└── vite.config.ts              Desarrollo y proxy local
iniciar.sh                      Lanzador para Linux, también desde fish
README.md                       Guía del proyecto
CONTEXTO_PROYECTO.md             Contexto para continuar con otro agente
AGENTS.md                       Convenciones de trabajo del repositorio
```

En cada módulo, `rutas.py` recibe peticiones, `esquemas.py` valida entradas, `servicios.py` aplica reglas y `repositorio.py` consulta o guarda. Diagnóstico no necesita esquemas de formulario propios.

## Preparación local

Requiere Python compatible con las dependencias fijadas, Node.js 22 o superior con npm y MySQL 8 o MariaDB 10.4 o superior. La instalación local utiliza MariaDB de XAMPP.

Desde la raíz en Linux:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

En Windows, PowerShell:

```powershell
py -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
npm --prefix web ci
Copy-Item backend/.env.example backend/.env
```

Crea la base `fym_pass` y una cuenta de base de datos dedicada. Completa `BD_HOST`, `BD_PUERTO`, `BD_USUARIO`, `BD_CLAVE` y `BD_NOMBRE` en `backend/.env`. Genera `CLAVE_QR` aleatoria de al menos 32 caracteres y consérvala: cambiarla invalida los carnets existentes. No publiques el archivo `.env`.

Con MySQL iniciado, aplica las migraciones desde `backend/`:

```sh
.venv/bin/python -m alembic upgrade head
```

En Windows usa `.\.venv\Scripts\python.exe` en lugar de `.venv/bin/python`. La revisión actual es **0005**. El arranque no migra ni reinicia los datos automáticamente.

### Datos iniciales opcionales

La instalación actual conserva 28 personas ficticias: 4 administrativos, 6 docentes y 18 estudiantes, además de los marcados realizados durante la validación. Cambiar la versión no reemplaza estos datos.

Para preparar ese conjunto en una base local nueva, desde `backend/`:

```sh
.venv/bin/python -m aplicacion.datos_iniciales --confirmar-base fym_pass
```

La herramienta exige `mysqldump` o `mariadb-dump`, crea un respaldo y rechaza la carga si ya hay personas. No se ejecuta al iniciar el sistema. `--actualizar-accesos` solo actualiza las cuentas del conjunto ficticio, revoca sus sesiones y pausa los puestos; `--reemplazar-usuarios` descarta personas e historial y requiere una decisión explícita del responsable. No combines estas dos opciones.

## Arranque

En Linux, desde Bash, fish o zsh:

```sh
./iniciar.sh
```

El script necesita Bash y Python 3; no se ejecuta con `fish iniciar.sh`. MySQL debe estar iniciado. `--sin-navegador` evita abrir el navegador y Ctrl+C cierra los procesos iniciados por el lanzador. Los registros quedan en `.registros/`.

En Windows, inicia MySQL en XAMPP y usa dos terminales PowerShell:

```powershell
cd D:\dev_\FyM_Pass\backend
.\.venv\Scripts\python.exe -m uvicorn aplicacion.main:aplicacion --host 127.0.0.1 --port 8000
```

```powershell
cd D:\dev_\FyM_Pass\web
npm run dev
```

En Linux también puedes iniciar manualmente Uvicorn con `.venv/bin/python` desde `backend/` y `npm run dev` desde `web/`. No repitas los comandos si los puertos ya están ocupados.

- Web local: `http://127.0.0.1:5173`.
- Documentación de la API: `http://127.0.0.1:8000/docs`.
- Salud del sistema: `/api/salud`; base de datos: `/api/salud/base-datos`.

## Uso de la jornada

1. Ingresa como administrador u operador y abre **Dispositivos y puesto**.
2. Elige QR dinámico, cámara o ambas modalidades e inicia la asistencia. Permite la ventana emergente y, si corresponde, la cámara.
3. Cada persona presenta su carnet a la cámara o escanea el QR del puesto desde su cuenta.
4. Consulta los marcados en Asistencia diaria; reportes y justificaciones conservan el historial.
5. Al finalizar, pausa el puesto. Cerrar su ventana no lo pausa. Reabrirlo reemplaza la credencial anterior.

El QR dinámico cambia cada 30 segundos. El puesto dispone de un token de hasta 16 horas en `sessionStorage`. Los estudiantes tienen una entrada al día; el personal, una entrada y una salida, sin reingresos. Repetir una lectura dentro de diez segundos devuelve el resultado existente y el UUID evita duplicar una solicitud. Retira el carnet de la cámara al menos 1,5 segundos antes de volver a mostrarlo.

Los horarios se confirman con fecha de inicio y conservan asignaciones anteriores. Cambiar la configuración de un grupo prepara un nuevo horario, pero no lo aplica hasta confirmar alumnos y fecha. Los horarios ya utilizados no se editan directamente: se copian y se reasignan. La migración 0005 conserva las asignaciones heredadas de alumnos existentes.

La cámara procesa imágenes en el navegador, sin grabarlas ni enviarlas al servidor. Las confirmaciones sonoras están activas y necesitan la primera interacción que permita el navegador.

## Teléfono, HTTPS e instalación PWA

Para cámara e instalación desde otro dispositivo se necesita HTTPS. Se puede usar un túnel temporal de Cloudflare. Con la API y MySQL activos, compila la web y abre Preview desde la raíz:

```sh
npm --prefix web run build
npm --prefix web run preview -- --host 127.0.0.1 --port 4173 --strictPort
```

En otra terminal:

```sh
cloudflared tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

En esta instalación de Windows, si no está en PATH:

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

Abre en el teléfono la URL HTTPS que imprime el túnel. Preview redirige `/api` a FastAPI; no se expone MySQL. Mantén PC, API, Preview y túnel activos; Ctrl+C detiene el acceso temporal. Un error 502 suele indicar que Preview no está disponible; si la web abre pero no accede, revisa API y base.

En iPhone, usa Safari y **Añadir a pantalla de inicio**. En Android y PC, usa **Instalar FyM Pass** o la opción del navegador. El service worker se registra en la compilación, no en desarrollo. Actualiza fuera de una sesión de marcado y cierra ventanas antiguas para que se active la nueva versión. Una instalación desde un túnel deja de conectar si el enlace cambia o se cierra.

La PWA cachea únicamente recursos públicos. No guarda carnets ni respuestas de la API y no tiene cola de marcados sin conexión. `./iniciar.sh --red auto` permite comprobar la API en red local, pero no configura HTTPS.

## Datos, acceso y respaldos

El rol institucional es distinto del permiso: administrador, operador o acceso personal. El backend autoriza cada operación. Las contraseñas usan scrypt; las sesiones duran ocho horas mediante cookie HttpOnly/SameSite Strict y la base guarda el resumen del token. En HTTPS permanente debe habilitarse `COOKIE_SEGURA`. El historial personal deriva su identidad de la sesión y no permite consultar otra persona.

Las credenciales completas se conservan en `README_CREDENCIALES.local.md` y `backend/.credenciales_beta.local.txt`, privados y excluidos de Git. El nombre del segundo archivo se mantiene por compatibilidad con los respaldos locales; no indica la versión del sistema. No hay credenciales públicas de acceso.

DBeaver se conecta a MariaDB/MySQL en `127.0.0.1:3306`, base `fym_pass`, con la cuenta privada de `.env`. Respalda la base antes de migraciones o mantenimiento. Conserva también `.env`, `CLAVE_QR` y `backend/archivos/` por un medio privado. La base, fotos históricas, credenciales y respaldos no viajan con Git.

Los eventos se guardan en UTC y se muestran en `America/Lima`. Las tablas principales agrupan identidad y sesiones, carreras/grupos, horarios/asignaciones, tolerancias/reglas, puestos/marcados, justificaciones, dispositivos, tarifas y auditoría. Alembic controla las revisiones.

## Alcance y siguientes etapas

La versión 1.0.0 es funcional y se ejecuta localmente. Mantiene datos ficticios hasta que administración defina su sustitución por datos institucionales. El despliegue con VPS, dominio y HTTPS permanente sigue pendiente.

- Los avisos en vivo y el límite de intentos de acceso funcionan en memoria de un único proceso de API; varios procesos requieren almacenamiento o mensajería compartidos.
- No hay sincronización offline ni carga retroactiva completa. El registro manual actual solo permite entradas de hoy con hora del servidor y rechaza ausencias ya evaluadas. Ante una caída se conserva un registro externo para revisión administrativa.
- Los filtros de carrera/ciclo/turno representan la asignación actual; su historial completo queda pendiente. No hay jornadas nocturnas ni reingresos.
- ZKTeco se conserva solo como inventario/configuración. La integración física no está implementada.
- Quedan pendientes recuperación autónoma de contraseñas, operación entre sedes y validación de despliegue, concurrencia y dispositivos reales.

La web conserva los temas claro y oscuro, azul institucional y controles compartidos. Por decisión del usuario, el repositorio no contiene suites de pruebas automatizadas ni Docker. Se verifica con compilación TypeScript/Vite y comprobaciones puntuales sin conservar archivos de prueba.

La documentación de uso y arquitectura se concentra en este README. El contexto para continuar el desarrollo está en [CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md); las convenciones para agentes permanecen en [AGENTS.md](AGENTS.md).
