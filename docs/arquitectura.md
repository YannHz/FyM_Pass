# Monolito modular con arquitectura por capas

FyM Pass sigue siendo un único servidor FastAPI. Sus funciones se agrupan en módulos y cada módulo separa la entrada HTTP, las reglas del negocio y la persistencia. React utiliza estos endpoints desde el navegador y la PWA.

```text
Web / PWA React
          ↓
Rutas y dependencias HTTP
          ↓
Servicios del módulo
          ↓
Repositorios
          ↓
MySQL / MariaDB
```

## Responsabilidades

| Parte | Qué hace | Qué no debe hacer |
| --- | --- | --- |
| rutas.py | Recibe parámetros y archivos, resuelve permisos y dependencias, configura cookies/encabezados y devuelve HTTP | Escribir SQL o decidir reglas de asistencia |
| esquemas.py | Valida tipos, tamaños, rangos y estructura de entrada con Pydantic | Conectar a la base o importar FastAPI |
| servicios.py | Aplica reglas, coordina operaciones, autoriza casos de uso y decide cuándo confirmar o revertir | Recibir Request/Response, usar Depends o construir consultas SQL |
| repositorio.py | Ejecuta consultas, bloqueos y operaciones de persistencia | Importar las rutas o decidir respuestas HTTP |
| infraestructura/ | Genera Excel y conserva infraestructura histórica de fotos | Recibir peticiones HTTP |
| compartido/ | Dependencias HTTP, errores de aplicación, firma QR y operaciones comunes de repositorio | Contener una segunda implementación de cada módulo |

La validación de tipos no sustituye las reglas del servicio. Por ejemplo, el esquema valida el formato de una hora y el servicio comprueba que la salida sea posterior a la entrada.

## Estructura actual

```text
backend/aplicacion/
├── main.py                 Compone la API, manejadores de errores y fotos públicas
├── config.py               Configuración privada por entorno
├── database.py             Motor SQLAlchemy
├── models.py               Entidades ORM y estructura de tablas
├── seguridad.py            Hash de contraseña y resumen de tokens
├── compartido/
│   ├── dependencias.py     Sesión por petición y permisos HTTP
│   ├── errores.py          Errores de aplicación y persistencia
│   ├── codigos_qr.py       Firma y comprobación de los QR
│   └── repositorio.py      Operaciones y transacciones comunes
├── modulos/
│   ├── acceso/
│   │   ├── rutas.py
│   │   ├── esquemas.py
│   │   ├── servicios.py
│   │   └── repositorio.py
│   ├── asistencia/
│   │   ├── dependencias.py Acceso del puesto por token
│   │   ├── rutas.py
│   │   ├── esquemas.py
│   │   ├── servicios.py
│   │   └── repositorio.py
│   ├── gestion/
│   │   ├── rutas.py
│   │   ├── esquemas.py
│   │   ├── servicios.py
│   │   └── repositorio.py
│   └── diagnostico/
│       ├── rutas.py
│       ├── servicios.py
│       └── repositorio.py
├── infraestructura/
│   ├── fotos.py            Validación, compresión y almacenamiento local
│   └── reportes.py         Construcción de libros XLSX
└── datos_beta.py           Preparación explícita de personas ficticias
```

Diagnóstico no necesita un esquema de entrada propio porque no recibe formularios. Los antiguos archivos acceso.py, asistencia.py, gestion.py y diagnostico.py de la raíz se sustituyeron por sus módulos. No volver a colocar allí la implementación.

Los modelos ORM permanecen compartidos y los servicios reciben repositorios concretos. Es una arquitectura clásica por capas, no una implementación hexagonal ni un dominio completamente independiente del ORM. Las consultas SQL de la API están en repositorios; los preparadores administrativos de datos ficticios conservan su acceso explícito como herramientas separadas del flujo HTTP.

## Ejemplo: marcar asistencia

1. La ruta recibe el QR y UUID con el esquema LecturaQR.
2. Las dependencias recuperan sesión o token del puesto y comprueban acceso.
3. El servicio comprueba firma, sede, modalidad, duplicados, horario y movimiento permitido.
4. El repositorio mantiene los bloqueos de filas, consulta y registra el marcado y su evento.
5. El servicio confirma la operación y devuelve el resultado.
6. La ruta lo expone con el mismo contrato que ya utilizan React.

La firma QR se comparte para que carné, expediente y lectura no mantengan versiones distintas de la misma regla. Asistencia consulta las reglas y horarios de Gestión utilizando un repositorio sobre la misma sesión, sin llamar a rutas HTTP internas.

## Transacciones, errores y archivos

Cada petición tiene una sesión SQLAlchemy compartida por sus dependencias. El servicio decide el límite de la operación; el repositorio ejecuta agregar, sincronizar, confirmar y revertir. Una excepción antes de confirmar provoca cierre/reversión de la sesión. Se mantienen los puntos de confirmación y bloqueos de la implementación anterior.

ErrorAplicacion representa un fallo esperado; main.py lo convierte en la respuesta HTTP con detail y código correspondiente. Los servicios no importan FastAPI. Los conflictos de integridad se traducen en persistencia y los mensajes concretos permanecen en los casos de uso. El manejador general evita exponer errores de la base.

La carga de fotos se retiró de la API y todas las pantallas muestran iniciales calculadas en compartido/identidad.py. El directorio backend/archivos/fotos y su infraestructura histórica se conservan para no borrar archivos previos. Excel se construye en infraestructura; el servicio selecciona filas y filtros y la ruta devuelve el archivo con sus encabezados originales.

## Estado actual y continuación

Beta funcional local 0.2.0-beta.3. Se conserva la organización por capas y las rutas funcionales. No hay suites de pruebas automatizadas ni configuración de contenedores en esta versión por decisión del usuario.

El arranque local sigue siendo iniciar.sh en Linux o Uvicorn/Vite manualmente. Para añadir una función, definir entrada en esquemas, reglas en servicios, consultas en repositorio y la ruta HTTP. Crear migraciones únicamente si cambia el modelo de datos.

Pendientes: despliegue permanente con dominio y HTTPS, respaldo externo y restauración, validación de dispositivos/navegadores, concurrencia, vigencia histórica de grupos y operación entre sedes. El acceso HTTPS temporal mediante Cloudflare ya fue utilizado en pruebas. Flutter queda descartado.

## Interfaz web

App.tsx coordina acceso y recuperación de sesión. PanelAdministrativo.tsx compone módulos; FormularioGestion.tsx concentra formularios y tramos de horarios, y componentesGestion.tsx reúne tablas, diálogos, consultas y estados. servicio.ts centraliza peticiones, errores y avisos de caducidad. Carné y puesto conservan pantallas separadas con el mismo backend.

## Base de datos

Migración vigente: 0004. Motor de esta instalación: MariaDB 10.4.32 de XAMPP. Alembic controla las revisiones; el arranque no migra ni reinicia datos.

| Tablas | Función |
| --- | --- |
| sedes, roles, personas, usuarios | Identidad, sede asignada, cuenta y permiso |
| sesiones_acceso | Resumen de token y caducidad de sesión |
| horarios, tramos_horarios, asignaciones_horarios, tolerancias_roles | Jornadas y vigencias; lunes=0, domingo=6, salida opcional |
| puntos_asistencia, puestos_abiertos, eventos_puesto | Modalidades QR, acceso temporal y confirmaciones |
| marcados | Entrada/salida, hora original, modalidad y trazabilidad |
| carreras, grupos | Organización institucional |
| justificaciones, dias_no_lectivos, reglas_sedes | Revisión de ausencias y reglas por sede |
| tarifas_docentes | Tarifas para preplanilla estimada |
| dispositivos | Configuración e inventario; sin integración física ZKTeco |
| auditoria | Responsable y detalle de operaciones |
| alembic_version | Revisión del esquema |

Los eventos se guardan en UTC y se presentan en America/Lima. Los tramos son horas locales; no se admiten jornadas nocturnas en esta versión. Las vigencias, sedes, permisos y duplicados se comprueban en servicios/repositorios. Las correcciones con historial completo y la vigencia histórica de grupos siguen pendientes.

## Acceso y seguridad

El rol institucional y el permiso son distintos. Una sola pantalla de acceso redirige a /administracion, /operacion o /mi-acceso según permiso. El backend vuelve a autorizar cada operación; no confía en el destino elegido por el cliente.

Contraseñas con scrypt y sal aleatoria. Sesión de ocho horas mediante cookie HttpOnly/SameSite Strict; solo se conserva el resumen SHA-256 del token en base. El cierre revoca la sesión; persona, usuario y sede deben seguir activos. El token no se guarda en localStorage.

Las escrituras exigen un encabezado propio y no se habilita CORS a otros orígenes. COOKIE_SEGURA controla Secure en la cookie; se debe habilitar en un entorno exclusivamente HTTPS. El límite inicial de diez intentos por minuto/dirección vive en memoria y no es compartido entre procesos. Antes del despliegue público se debe definir proxy y control compartido de intentos.

Un 401 protegido abre la renovación de la misma cuenta sin desmontar el formulario. Al renovar se actualizan las consultas; ninguna escritura fallida se reenvía automáticamente. Salir del espacio descarta el borrador. La recuperación autónoma de contraseña está pendiente.

## Historial personal

GET /api/mi-asistencia requiere sesión y recibe solo el mes. El servicio obtiene persona/sede desde la cuenta, valida periodo hasta hoy y delega en filas_diarias con persona_id. Las consultas de personas, marcados y justificaciones filtran esa identidad en SQL. La respuesta expone solo fecha, entrada, salida y estado, con Cache-Control no-store. Los permisos administrativos no cambian. EspacioPersonal.tsx coordina carné e historial por fragmento de URL; MisAsistencias.tsx presenta mes, resumen y días.

## Jornada en vivo

GET /api/gestion/diario conserva su contrato completo para reportes y admite solo_marcados=true para la jornada. En ese modo el repositorio selecciona personas con marcados en el intervalo local convertido a UTC; el servicio elimina días sin movimientos y ordena por último marcado. La opción también se aplica al Excel. La respuesta diaria lleva Cache-Control no-store. useDatos admite consulta periódica sin superponer peticiones, conserva datos durante el refresco y cancela las consultas al desmontar/cambiar ruta. PanelAdministrativo controla el cambio de fecha local, conservando las consultas históricas elegidas por el usuario.

Los avisos de asistencia funcionan en memoria con un único proceso de API, incluyendo QR y registro manual después del commit. Son compatibles con el túnel HTTPS temporal. Al reconectar se recupera la tabla; si falla la conexión se reintenta cada tres segundos. Antes de usar varios procesos se requiere un canal compartido de avisos.
