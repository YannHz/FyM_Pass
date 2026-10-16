# Monolito modular con arquitectura por capas

FyM Pass sigue siendo un único servidor FastAPI. Sus funciones se agrupan en módulos y cada módulo separa la entrada HTTP, las reglas del negocio y la persistencia. React y Flutter siguen utilizando los mismos endpoints.

```text
Web React / App Flutter
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
| infraestructura/ | Procesa/almacena fotos y genera archivos Excel | Recibir peticiones HTTP |
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
├── datos_demo.py           Preparación explícita de cuentas ficticias
└── horarios_demo.py        Preparación explícita de horarios ficticios
```

Diagnóstico no necesita un esquema de entrada propio porque no recibe formularios. Los antiguos archivos acceso.py, asistencia.py, gestion.py y diagnostico.py de la raíz se sustituyeron por sus módulos. No volver a colocar allí la implementación.

Los modelos ORM permanecen compartidos y los servicios reciben repositorios concretos. Es una arquitectura clásica por capas, no una implementación hexagonal ni un dominio completamente independiente del ORM. Las consultas SQL de la API están en repositorios; los preparadores administrativos de datos demo conservan su acceso explícito como herramientas separadas del flujo HTTP.

## Ejemplo: marcar asistencia

1. La ruta recibe el QR y UUID con el esquema LecturaQR.
2. Las dependencias recuperan sesión o token del puesto y comprueban acceso.
3. El servicio comprueba firma, sede, modalidad, duplicados, horario y movimiento permitido.
4. El repositorio mantiene los bloqueos de filas, consulta y registra el marcado y su evento.
5. El servicio confirma la operación y devuelve el resultado.
6. La ruta lo expone con el mismo contrato que ya utilizan React y Flutter.

La firma QR se comparte para que carné, expediente y lectura no mantengan versiones distintas de la misma regla. Asistencia consulta las reglas y horarios de Gestión utilizando un repositorio sobre la misma sesión, sin llamar a rutas HTTP internas.

## Transacciones, errores y archivos

Cada petición tiene una sesión SQLAlchemy compartida por sus dependencias. El servicio decide el límite de la operación; el repositorio ejecuta agregar, sincronizar, confirmar y revertir. Una excepción antes de confirmar provoca cierre/reversión de la sesión. Se mantienen los puntos de confirmación y bloqueos de la implementación anterior.

ErrorAplicacion representa un fallo esperado; main.py lo convierte en la respuesta HTTP con detail y código correspondiente. Los servicios no importan FastAPI. Los conflictos de integridad se traducen en persistencia y los mensajes concretos permanecen en los casos de uso. El manejador general evita exponer errores de la base.

Las rutas de fotos leen el archivo y delegan el procesamiento a un hilo; el servicio coordina persona, almacenamiento y auditoría. El directorio sigue siendo backend/archivos/fotos. Excel se construye en infraestructura; el servicio selecciona filas y filtros y la ruta devuelve el archivo con sus encabezados originales.

## Compatibilidad y verificación

- No se modificaron tablas, migraciones, datos existentes ni el frontend.
- No cambian URLs, campos, cookies, encabezados no-store o reglas aprobadas.
- Se conserva el contrato OpenAPI anterior en pruebas/contratos/openapi.json y se compara completo en test_capas.py: 34 rutas y sus esquemas.
- Las pruebas verifican separación de imports: servicios y esquemas sin HTTP ni construcción SQL; repositorios sin importar rutas o servicios.
- Se prueban además carga de foto en un directorio temporal, foto inválida, permisos, reversión completa de cambios y diagnóstico de base.
- Última comprobación de esta reorganización: 33 pruebas backend y 18 frontend correctas, compilación web correcta y alembic check sin diferencias en MariaDB. Las pruebas de backend utilizan SQLite temporal; no acreditan concurrencia de MySQL real.

El arranque continúa siendo iniciar.sh en Linux, por decisión del usuario. MySQL debe estar activo. La política de secretos, HTTP de demo, SDK Android y configuración de Flutter no cambia.

## Cómo continuar

Para añadir una función, definir la entrada en esquemas, la regla en servicios, las consultas en repositorio y finalmente la ruta. Probar la regla con un repositorio simulado y el recorrido con base temporal. Solo crear migraciones si realmente cambia el modelo de datos.

La demo ya fue aprobada por administración. Antes de producción siguen pendientes HTTPS, copias/restauración, firma Android, vigencia histórica de grupos, carga/concurrencia y operación multi-sede. Organizar el código no resuelve por sí solo esos pendientes.
