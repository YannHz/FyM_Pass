# FyM Pass

Demo de asistencia de ingreso al Instituto de Educación Superior Técnica Finney Miller. Incluye administración web y aplicación Android Flutter. Actualmente opera en la sede principal.

## Tecnologías y arquitectura

| Capa | Tecnologías |
| --- | --- |
| Web | React 19, TypeScript, Vite, Tailwind CSS, Lucide, QRCode y ZXing |
| API | Python, FastAPI, Uvicorn, Pydantic |
| Persistencia | MySQL/MariaDB, SQLAlchemy, PyMySQL y Alembic |
| Android | Flutter, Dart, mobile_scanner y flutter_secure_storage |
| Reportes | openpyxl para XLSX; Pillow para fotos |
| Pruebas | unittest, Vitest y Testing Library; flutter test |

Arquitectura de monolito modular: `Web React / App Flutter → API FastAPI → MySQL/MariaDB`. Solo la API accede a la base. Vite mantiene la web en localhost y redirige `/api` al servidor configurado. La API puede escuchar en la IP privada de la PC para Flutter. Los datos se guardan en UTC y se muestran según la zona de la sede, actualmente Lima.

El código móvil está en otro proyecto, `FyM_Pass_Movil`; esta carpeta `mobile/` solo documenta su relación. Para subir ambos, usa dos repositorios o incorpora explícitamente el móvil a una estructura común. Clonar este repositorio no incluye automáticamente la app móvil ni datos locales.

## Funcionalidades

- Acceso con usuario y contraseña; destino y permisos según cuenta.
- Carné virtual y QR dinámico del puesto, con modalidades configurables.
- Estudiantes: entrada. Docentes y administrativos: entrada y salida.
- Confirmación de tres segundos, foto o iniciales, nombre, rol, movimiento, hora y resultado.
- Resumen, dispositivos, diario, manual auditado, reportes Excel, preplanilla estimada, justificaciones, personas/carnés, carreras/horarios y tolerancias/reglas.
- Temas claro, oscuro y del sistema; preferencias de transparencia, navegación adaptable y transiciones con reducción de movimiento.

ZKTeco es inventario/configuración; no hay integración física. La preplanilla es referencial. La asistencia al instituto no determina asistencia a clases ni sanciones académicas.

## Requisitos y primera instalación

Python 3.11 o superior compatible con las dependencias, Node.js 22 LTS y npm. MySQL 8 o MariaDB 10.4 o superior. El arranque requiere MySQL activo y dependencias instaladas; no instala programas, no inicia MySQL con privilegios ni aplica migraciones automáticamente.

### Linux

Instala Python, pip/venv, Node/npm y MySQL/MariaDB mediante tu distribución. No necesitas activar el entorno virtual:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

Si una versión fijada no tiene soporte para tu Python/arquitectura, usa `backend/requirements.txt` y verifica pruebas. Los lockfiles permanecen versionados.

### Preparar la base

Con un administrador de MySQL/MariaDB, crea una base local y un usuario dedicado. Sustituye la contraseña de ejemplo por una propia:

```sql
CREATE DATABASE fym_pass CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fym_pass'@'127.0.0.1' IDENTIFIED BY 'CAMBIAR_POR_CLAVE_LOCAL';
GRANT ALL PRIVILEGES ON fym_pass.* TO 'fym_pass'@'127.0.0.1';
```

Edita `backend/.env`: host `127.0.0.1`, puerto `3306`, base y usuario `fym_pass`, tu contraseña y `CLAVE_QR` aleatoria de al menos 32 caracteres. Para generarla sin compartirla: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`. Conserva la clave mientras quieras mantener válidos los carnés.

Desde `backend`, ejecuta estos tres comandos usando el Python correspondiente:

```bash
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m aplicacion.datos_demo
.venv/bin/python -m aplicacion.horarios_demo
```

Las migraciones crean estructura y catálogos iniciales; las cuentas y horarios demo se preparan aparte. Las contraseñas se generan aleatoriamente y se guardan en `backend/.credenciales_demo.local.txt`. No ejecutar estos preparadores sobre datos institucionales sin revisar su alcance.

## Arrancar con un comando

Desde la raíz del proyecto, en Bash, fish o zsh:

```bash
./iniciar.sh
```

Para presentar también la aplicación Flutter por Wi-Fi, conecta primero la laptop a la misma red que el teléfono y ejecuta:

```bash
./iniciar.sh --red auto
```

También puedes indicar la IPv4 privada de tu laptop con `./iniciar.sh --red 192.168.1.100`. Si usas otra carpeta de trabajo, ejecuta el script por su ruta absoluta. Consulta las opciones con `./iniciar.sh --help`.

El único lanzador es `iniciar.sh` y requiere Bash y Python 3. Inicia API y web, verifica la conexión a MySQL y abre el navegador cuando los servicios están disponibles. `--sin-navegador` evita abrirlo. Mantén la terminal abierta; Ctrl+C detiene los servicios iniciados por el script. Los registros quedan en `.registros/backend.log` y `.registros/web.log`. Si los puertos 8000/5173 están ocupados, cierra la instancia anterior.

Usa en Flutter la dirección `API / Flutter` que muestra la terminal. Si cambia la IP de la laptop, actualiza el servidor en Flutter y revisa el permiso HTTP de Android. La detección automática depende de la ruta de red activa; una VPN puede cambiarla.

La web está en `http://127.0.0.1:5173`; la documentación API en `http://IP_PC:8000/docs`. El modo red no configura el firewall; en Linux adapta las reglas al firewall de tu distribución y permite únicamente TCP 8000 desde la red local. MySQL no necesita exponerse.

## Credenciales de acceso

| Cuenta | Uso |
| --- | --- |
| `admin.demo` | Administración completa web; identidad administrativa en móvil |
| `operador.demo` | Operación del puesto y cargas permitidas |
| `docente.demo` | Carné web/móvil y entrada/salida |
| `estudiante.demo` | Carné web/móvil y entrada |

Web y Flutter usan las mismas cuentas y contraseñas. Las contraseñas actuales y la conexión de base de esta instalación están en **`README_CREDENCIALES.local.md`**, excluido de Git. El clon genera sus propias cuentas mediante `datos_demo`; no depende de contraseñas publicadas ni copia las sesiones anteriores. La base usa los valores de `backend/.env`, también excluido. Nunca subas estos archivos, fotos ni volcados con información real.

Si quieres conservar los datos de prueba entre PCs, realiza una exportación privada de MySQL/MariaDB y transfiere también las fotos y la configuración necesaria por un medio privado. Git no transporta la base ni archivos ignorados. No vuelvas a generar cuentas demo sobre una base importada.

## Flutter por Wi-Fi

La PC y el teléfono deben compartir red. Ejecuta el lanzador con `--red IP_PC`, comprueba `http://IP_PC:8000/api/salud` desde el teléfono y configura esa dirección en **Conexión de la demo → Servidor** de Flutter. Ya se probó sin cable usando el punto de acceso del teléfono.

Android limita el HTTP de la demo a direcciones explícitas en `android/app/src/main/res/xml/network_security_config.xml` del proyecto móvil. Si cambia la IP al usar la ThinkPad, actualiza ese archivo y recompila/reinstala el APK, o utiliza un endpoint HTTPS. Cambiar solo el campo Servidor puede no bastar. No abrir esta demo HTTP a internet.

El carné descargado puede mostrarse offline; el marcado desde el móvil necesita servidor y red disponibles. No existe una cola móvil de marcados offline.

## Verificación

Web: `npm --prefix web test` y `npm --prefix web run build`. Backend, desde su carpeta: `PYTHON_DEL_ENTORNO -m unittest discover -s pruebas` y `PYTHON_DEL_ENTORNO -m alembic check`. Móvil: `flutter analyze`, `flutter test`, `flutter build apk --debug` en su propio proyecto.

Última comprobación: 22 pruebas backend y 8 frontend correctas, compilación web correcta y esquema sin migraciones pendientes. Antes de producción faltan HTTPS, copias/restauración verificadas, configuración institucional, firma Android de distribución, vigencia histórica de grupos y operación entre sedes.

## Preparar la presentación

El resumen incluye diagnóstico independiente de API y base, dirección Flutter en modo red y un recorrido desplegable de la demo. Consulta [docs/recorrido_demo.md](docs/recorrido_demo.md) para preparar horarios y verificar los casos sin borrar registros. Este avance pasó 24 pruebas backend y 15 frontend.
