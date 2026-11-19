# FyM Pass

Sistema web de asistencia de ingreso al Instituto de Educación Superior Tecnológico Finney y Miller. Versión funcional **1.0.0**, con ejecución local y acceso desde navegador o PWA.

Actualizado el **18 de noviembre de 2026**. El sistema registra una entrada y una salida general por día de **docentes y personal administrativo**. Carrera y turno organizan los horarios; no generan marcados por clase ni entradas adicionales. La operación actual corresponde a la sede principal.

## Funciones y permisos

| Cuenta | Alcance |
| --- | --- |
| Administradora | Gestión de personas, horarios, reglas, preplanilla, seguridad y revisión de justificaciones |
| Operadora / secretaria | Puesto QR, consultas, registro manual y solicitudes de justificación |
| Personal | Carné virtual, marcado propio e historial personal |

El rol institucional (docente o administrativo) es diferente del permiso de la cuenta. Las secretarias y administradoras tienen rol administrativo.

- Puesto con QR dinámico y lectura de carné por cámara; modalidades configurables.
- Jornada diaria, reportes Excel, justificaciones, tolerancias y calendario institucional.
- Horarios separados entre docentes (carrera y turno) y personal administrativo (turno), con asignación desde una fecha.
- Cambiar un horario utilizado conserva la versión anterior; después se confirma la nueva asignación.
- Preplanilla docente estimada, sin pago ni descuentos automáticos.
- No hay integración física ZKTeco, operación multisede ni cola de marcados sin servidor.

## Tecnología y estructura

React 19, TypeScript, Vite 6, Tailwind CSS 4, Lucide, qrcode.react y ZXing. Backend Python/FastAPI, SQLAlchemy, PyMySQL, Alembic, Argon2id, cryptography y openpyxl. Persistencia MySQL/MariaDB.

Monolito modular por capas: navegador/PWA → API → servicios → repositorios → MySQL/MariaDB. Solo el backend accede a la base.

```text
backend/
  aplicacion/
    main.py                    API, errores y cabeceras
    models.py                  modelos y restricciones
    config.py / database.py    configuración y conexión
    seguridad.py               hash y política de contraseñas
    administrar_seguridad.py   claves, respaldos y recuperación local
    datos_iniciales.py         carga ficticia opcional
    compartido/                dependencias, identidad y firma QR
    infraestructura/           reportes Excel
    modulos/
      acceso/                  autenticación, sesiones y auditoría
      asistencia/              puesto, carnés y marcados
      gestion/                 personas, horarios y administración
      diagnostico/             salud y conexión
  migraciones/versiones/       0001 a 0009
  requirements.txt / requirements.lock
  .env.example                ejemplo sin secretos
web/
  src/                        pantallas y controles React
  public/                     manifest, iconos y página sin conexión
  pwa.ts / service-worker.js  preparación y caché pública
  vite.config.ts              proxy local y cabeceras de Preview
iniciar.sh                    lanzador Bash para Linux/macOS
AGENTS.md                     convenciones de trabajo
CONTEXTO_PROYECTO.md           traspaso para el agente
```

## Seguridad y acceso

El usuario se genera con inicial del primer nombre + primer apellido + `fym`, en minúsculas y sin tildes. Ante coincidencia se añaden las iniciales de los apellidos restantes; otra coincidencia requiere revisar los datos con administración.

- Contraseña inicial: primer nombre + inicial de cada apellido, todo en minúsculas y sin tildes. Ejemplo: Ana María Pérez Rojas → usuario `aperezfym`, clave inicial `anapr`. Es válida por 48 horas y exige cambio al primer ingreso; el mínimo de ocho caracteres se aplica a la nueva contraseña personal. El restablecimiento administrativo vuelve a emitir la clave inicial y renueva su vigencia.
- Contraseña personal de **8 a 256 caracteres**, confirmada dos veces. Se permiten espacios; se rechazan patrones comunes, repeticiones y datos personales. No se exige una mezcla fija de símbolos y números.
- Argon2id para hashes nuevos. Los hashes scrypt anteriores se actualizan al autenticar correctamente.
- Acceso con usuario y contraseña para todos los perfiles. El MFA y los códigos de recuperación se retiraron por decisión del proyecto; no se necesita una aplicación autenticadora.
- Sesión de hasta ocho horas, con vencimiento tras 30 minutos sin interacción y aviso previo. Las consultas automáticas no prolongan la actividad.
- Límites persistentes por cuenta y por IP, con esperas progresivas.
- Reautenticación para cambiar contraseñas, cerrar otras sesiones, modificar permisos, emitir accesos temporales o renovar carnés.
- Permisos aplicados en la API, cookie HttpOnly/SameSite Strict, cabecera propia en mutaciones y respuestas privadas sin caché.
- Auditoría de accesos y operaciones sensibles; alertas al acumular cinco rechazos QR similares en 15 minutos.
- Las fotos históricas requieren autenticación y autorización; ya no se cargan fotos nuevas desde la interfaz.

En **Cuenta → Seguridad de mi cuenta** están las sesiones y la contraseña. Las administradoras también pueden restablecer accesos, revocar carnés y consultar eventos.

El QR del puesto rota cada 30 segundos y está firmado. El carné es fijo hasta su revocación. Estas medidas no impiden fotografiar un carné ni reenviar un QR vigente: la comprobación presencial sigue dependiendo de la supervisión del puesto.

HTTP y la configuración de cookie Secure se mantienen por decisión del proyecto. Preview aplica CSP y otras cabeceras al frontend; si se utiliza otro servidor, hay que trasladar esa configuración. No se ha realizado un despliegue público.

## Base de datos

**La definición publicable de la base está en las migraciones Alembic y los modelos**, no en un volcado local. Revisión vigente: `0009`. Hay 23 tablas de aplicación, más `alembic_version`.

| Tablas | Finalidad |
| --- | --- |
| `sedes`, `roles` | Institución y roles institucionales |
| `personas`, `usuarios` | Identidad, permiso, hash, vigencia temporal y estado del cambio obligatorio de contraseña |
| `horarios`, `tramos_horarios`, `asignaciones_horarios` | Carrera, tipo de personal, turno, días, horas y vigencias |
| `tolerancias_roles`, `reglas_sedes`, `dias_no_lectivos` | Evaluación de puntualidad, ausencia y calendario |
| `puntos_asistencia`, `puestos_abiertos`, `eventos_puesto` | Puesto operativo, token resumido y resultado de lecturas |
| `marcados` | Entrada/salida, modalidad, responsable y resultado original |
| `sesiones_acceso` | Tokens resumidos, vencimiento y última actividad |
| `eventos_seguridad`, `limites_acceso` | Auditoría de seguridad y límites persistentes |
| `justificaciones`, `tarifas_docentes` | Revisión de incidencias y tarifa referencial |
| `dispositivos`, `auditoria` | Inventario y trazabilidad administrativa |
| `carreras`, `grupos` | Compatibilidad histórica del esquema; sin flujo de alumnado |

Las tablas históricas y el rol antiguo de estudiante se conservan para compatibilidad de migraciones y referencias; no habilitan acceso ni marcado estudiantil. La carrera de un horario docente se guarda actualmente como texto en `horarios.carrera`.

| Migración | Cambio |
| --- | --- |
| 0001 | Estructura inicial y catálogos |
| 0002 | Sesiones de acceso |
| 0003 | Puestos y carnés |
| 0004 | Administración, horarios y reportes |
| 0005 | Asignaciones heredadas de horarios |
| 0006 | Cambio obligatorio de contraseña |
| 0007 | Tipo de personal, carrera y turno de horarios |
| 0008 | Refuerzo de acceso, vigencia temporal, actividad de sesión, eventos y límites |
| 0009 | Retirada del MFA y sus columnas; conserva contraseñas, cuentas y asistencias |

Los eventos se guardan en UTC; los horarios son horas locales y la interfaz usa Lima. Se conserva el resultado original del marcado. No se soportan tramos que crucen medianoche.

La instalación ficticia puede crear **4 secretarias operadoras, 2 administradoras y 10 docentes**, con horarios de lunes a viernes y sin asistencias precargadas. Sus contraseñas se generan en cada carga; no existen credenciales universales en GitHub. La carga rechaza una base con personas existentes salvo opciones destructivas explícitas, que no deben utilizarse sobre datos a conservar.

## Instalación después de clonar

### 1. Dependencias y entorno

Se verificó el desarrollo en Windows con Python 3.14 y MariaDB 10.4.32 de XAMPP. Para Linux/macOS se proporciona el lanzador; no se ha validado una instalación nativa completa en esos sistemas. Se necesita Node.js 22 o superior y Python compatible con el lock.

Desde la raíz, en PowerShell:

```powershell
py -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
npm --prefix web ci
Copy-Item backend/.env.example backend/.env
```

En Linux/macOS:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

No sobrescribir un `backend/.env` existente. Configurarlo privadamente con host, puerto, base, usuario operativo y contraseña. Generar `CLAVE_QR` aleatoria de al menos 32 caracteres. Mantener esa clave si se conservarán carnés existentes.

`INACTIVIDAD_MINUTOS=30` controla la sesión. La API no requiere claves de autenticador. `clave_respaldos.key` se utiliza únicamente para proteger respaldos y listados privados.

`PROXY_CONFIABLE=false` usa la IP directa. Habilitarlo solo tras un proxy configurado para sobrescribir las cabeceras de origen. `COOKIE_SEGURA` conserva su configuración actual; el lanzador no la cambia.

### 2. Base y preparación de seguridad

El clon no contiene la base local, usuarios SQL, claves ni respaldos. Un responsable de MySQL/MariaDB debe crear `fym_pass` con `utf8mb4` y la cuenta operativa configurada en `.env`.

Para la preparación inicial, esa cuenta puede tener permisos de esquema sobre **esta base únicamente**. Después se separan los permisos. No usar `root` como cuenta operativa de la app.

Desde `backend`:

```powershell
.\.venv\Scripts\python.exe -B -m alembic upgrade head
.\.venv\Scripts\python.exe -B -m aplicacion.administrar_seguridad claves
```

En Linux/macOS, reemplazar `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

Para respaldos y preparación de permisos se necesita una cuenta administrativa SQL local. Si ya tiene contraseña, configurar privadamente `backend/archivos/seguridad/administracion_bd.local.json` con las propiedades `usuario` y `clave`, y volver a ejecutar `claves` para proteger sus permisos de archivo. Esta cuenta es de la base, distinta de las cuentas de la interfaz.

La herramienta contempla un XAMPP local recién instalado con `root` sin contraseña cuando ese archivo aún no existe. Al ejecutar lo siguiente protege el acceso administrativo, crea la cuenta `fym_migracion` y reduce la cuenta operativa a SELECT/INSERT/UPDATE/DELETE:

```powershell
.\.venv\Scripts\python.exe -B -m aplicacion.administrar_seguridad preparar
```

`preparar` realiza un respaldo cifrado antes de modificar permisos. Está limitado a la base `fym_pass` en localhost y requiere privilegios administrativos SQL y `mariadb-dump` o `mysqldump`. En Linux con autenticación de root por socket, el responsable debe proporcionar una cuenta administrativa compatible con conexión local TCP; la herramienta no configura ese acceso del sistema.

En XAMPP ya protegido, phpMyAdmin debe usar autenticación por cookie y una contraseña no vacía. El archivo de acceso SQL privado no debe copiarse al repositorio.

### 3. Migraciones posteriores

Después de separar los permisos, utilizar la cuenta de migraciones. Desde `backend`, en PowerShell:

```powershell
$env:FYM_MIGRACION = "1"
.\.venv\Scripts\python.exe -B -m alembic upgrade head
.\.venv\Scripts\python.exe -B -m alembic check
Remove-Item Env:FYM_MIGRACION
```

En Bash:

```sh
FYM_MIGRACION=1 .venv/bin/python -B -m alembic upgrade head
FYM_MIGRACION=1 .venv/bin/python -B -m alembic check
```

En fish, usar `env FYM_MIGRACION=1 .venv/bin/python -B -m alembic upgrade head`. No ejecutar migraciones automáticamente al arrancar ni utilizar las credenciales administrativas para servir la API.

### 4. Carga ficticia opcional y primer ingreso

Solo para una base vacía, desde `backend`:

```powershell
.\.venv\Scripts\python.exe -B -m aplicacion.datos_iniciales --confirmar-base fym_pass
```

Se crea un respaldo previo y se muestra la ruta del listado cifrado de accesos iniciales. Para verlo localmente:

```powershell
.\.venv\Scripts\python.exe -B -m aplicacion.administrar_seguridad mostrar-accesos --archivo RUTA_DEL_LISTADO.local.md.fernet
```

El listado se muestra en esa terminal privada; no pegarlo en incidencias ni subir capturas. Las contraseñas caducan a las 48 horas. El flujo normal de creación/restablecimiento desde la web muestra la contraseña una sola vez y no genera un listado.

La primera administradora cambia su contraseña temporal y accede directamente al panel. Las demás cuentas pueden gestionarse desde Cuenta → Seguridad.

## Arranque diario

MySQL/MariaDB debe estar activo. El lanzador no instala dependencias, inicia MySQL, modifica permisos, ejecuta migraciones ni carga datos.

En Linux/macOS, desde Bash o fish:

```sh
./iniciar.sh
./iniciar.sh --sin-compilar --sin-navegador
./iniciar.sh --desarrollo
./iniciar.sh --red auto
```

- Modo normal: compila y sirve la web en 4173; API en localhost:8000.
- `--sin-compilar`: exige un `web/dist` completo y vigente.
- `--desarrollo`: puerto 5173, sin PWA; se mantiene en localhost.
- `--red auto|IP`: publica únicamente la web compilada en una IPv4 privada; la API permanece local.
- `--sin-navegador`: no abre una ventana.
- Comprueba dependencias, claves, conexión SQL, revisión Alembic y coincidencia de versiones.
- La disponibilidad SQL se comprueba desde el backend, sin consultar anónimamente rutas autenticadas ni iniciar sesión con una cuenta.
- Ctrl+C detiene solo los procesos creados por el lanzador. No cierra MySQL ni mata instancias ajenas.
- Registros en `.registros/`. No iniciar otra instancia si los puertos están ocupados.

En Windows se mantienen los comandos manuales, en dos terminales desde la raíz:

```powershell
# terminal de la API
Set-Location backend
.\.venv\Scripts\python.exe -B -m uvicorn aplicacion.main:aplicacion --host 127.0.0.1 --port 8000
```

```powershell
# terminal de la web
npm --prefix web run build
Set-Location web
node .\node_modules\vite\bin\vite.js preview --host 127.0.0.1 --port 4173 --strictPort
```

La carpeta de trabajo de Vite es `web`; ejecutarlo en la raíz puede provocar que no encuentre `dist`. Abrir [FyM Pass](http://127.0.0.1:4173). API: [documentación local](http://127.0.0.1:8000/docs). `/api/salud` indica vida de la API; no demuestra disponibilidad SQL. `/api/salud/base-datos` exige sesión de encargado y los controles de acceso completados.

Para un acceso temporal desde teléfono, con los servicios ya activos y solo cuando se solicite:

```sh
cloudflared tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

La URL cambia al recrear el túnel. La cámara y la instalación móvil necesitan un contexto seguro. No exponer el servidor de desarrollo ni MySQL. No hay despliegue VPS configurado.

La PWA almacena recursos públicos, no respuestas de la API. Una actualización muestra el aviso flotante “FyM Pass se actualizó”; la recarga es manual para preservar formularios abiertos.

La disponibilidad de instalación se captura desde el arranque, incluso antes de abrir Cuenta. Cuando el navegador la habilita, **Instalar FyM Pass** abre directamente su confirmación nativa. Si no está disponible, **Cómo instalar FyM Pass** muestra ayuda para el dispositivo. En iPhone/iPad se utiliza Compartir en Safari. La confirmación final corresponde al usuario; instalar no habilita operaciones sin conexión.

## Respaldos y recuperación

Desde `backend`:

```powershell
.\.venv\Scripts\python.exe -B -m aplicacion.administrar_seguridad respaldo
.\.venv\Scripts\python.exe -B -m aplicacion.administrar_seguridad recuperar-admin --usuario NOMBRE_DE_CUENTA
```

La segunda orden es una recuperación administrativa local excepcional: invalida sesiones y muestra un acceso temporal una sola vez. Usarla tras verificar la identidad del titular.

Los respaldos nuevos se guardan como `.sql.fernet`. `clave_respaldos.key` permite descifrarlos. Conservar claves históricas privadas si se necesitan para restaurar respaldos anteriores; no se usan en el inicio de sesión actual. Los datos cifrados sin sus claves no bastan para recuperar la instalación. Custodiar las claves por separado de una copia externa del respaldo.

La base, `.env`, claves y archivos de `backend/archivos/seguridad/` son privados. La herramienta aplica permisos del usuario local y SYSTEM en Windows; 0700 a la carpeta y 0600 a archivos en POSIX. No sobrescribirlos al actualizar el código.

Se verificó una restauración de 16 cuentas en una base aislada de MariaDB, posteriormente retirada. La copia externa, conservación mensual y nuevas comprobaciones de restauración son responsabilidad operativa; no hay automatización de esas tareas. Los históricos protegidos conservan su nombre más `.fernet`, y no se borran automáticamente.

## Verificaciones y límites

- Compilación TypeScript/Vite.
- Migraciones hasta 0009 y `alembic check` sin diferencias en la instalación local verificada.
- Comprobaciones aisladas del acceso sin MFA, contraseñas, permisos, límites persistentes e inactividad.
- Restauración de respaldo cifrado sobre una base de prueba.
- Política actual de 8 caracteres verificada: acepta una clave válida de ocho y rechaza siete caracteres y patrones débiles.
- No hay suites de pruebas versionadas ni Docker por decisión del proyecto.
- No se afirma una certificación ni una prueba de penetración completa.
- Auditoría del lock Python y de dependencias frontend de producción sin vulnerabilidades conocidas al revisarlas el 18/11/2026. El árbol completo npm conserva un aviso en picomatch 4.0.7, dependencia de desarrollo sin parche publicado en el registro consultado. No degradar Vite para ocultarlo.
- Pendientes: despliegue estable, supervisión y copias externas, pruebas de carga, múltiples sedes y validación física en los dispositivos de destino.

## Qué publicar en GitHub

Publicar fuentes, migraciones 0001–0009, locks, `backend/.env.example`, lanzador y documentación. Las migraciones permiten reconstruir el esquema; la carga ficticia es opcional y genera credenciales nuevas.

No publicar `.env`, claves, credenciales SQL, listados de acceso, volcados, archivos cifrados de respaldo, fotos, registros de ejecución, entornos, `node_modules` ni `dist`. El cifrado no convierte un respaldo en un archivo público.

Antes de subir:

```sh
git status --short
git diff --check
git ls-files backend/archivos database backend/.env README_CREDENCIALES.local.md
```

La última orden no debe listar datos privados. `.gitignore` no elimina archivos ya versionados ni borra el historial: si alguna clave llegó a publicarse, retirarla del historial y rotarla mediante un procedimiento acordado. Este trabajo no realiza commit ni push.
