# Revisión del proyecto — 12 de octubre de 2026

## Estructura y alcance

La web usa React y TypeScript con Vite; se comunica por rutas `/api` que Vite redirige a FastAPI. La API usa SQLAlchemy y MySQL/MariaDB, con cuatro migraciones Alembic. Flutter vive en un proyecto separado; `mobile/` contiene documentación.

El backend separa acceso, marcado QR y gestión administrativa. Hay rutas para personas, carreras, grupos, horarios, diario, carga manual, justificaciones, reglas, días no lectivos, dispositivos, expediente, preplanilla y exportación. La revisión del código confirma contraseñas con scrypt, sesiones almacenadas como hashes, cookies HttpOnly, permisos por cuenta, auditoría manual y bloqueos de filas en operaciones de marcado. Esta revisión no sustituye una auditoría integral ni una prueba de concurrencia sobre MySQL.

## Corrección del inicio

La shell utilizada es fish. Se restauró `iniciar.fish` con un intérprete explícito y ejecución directa de Python; el README indica `fish iniciar.fish`. Se comprobó que resuelve la raíz desde otra carpeta, conserva los argumentos y devuelve el código de salida de Python. `iniciar.sh` queda disponible para Bash. El lanzador Python informa qué requisitos faltan y rechaza una IP mal formada sin mostrar una excepción interna.

## Verificación y pendientes

- Las doce pruebas web y la compilación TypeScript/Vite pasaron.
- Las 22 pruebas backend pasaron con una clave temporal de pruebas en el entorno. Las pruebas QR necesitan `CLAVE_QR` de al menos 32 caracteres; sin esa configuración responden 503. No se escribieron credenciales.
- Tras cargar el lector bajo demanda, el paquete inicial mide aproximadamente 323 kB (100 kB gzip) y el lector separado 414 kB (109 kB gzip). La compilacion ya no muestra la advertencia de paquetes superiores a 500 kB.
- Se completó el montaje local con MariaDB de XAMPP: base `fym_pass`, usuario dedicado, `.env` privado, cuatro migraciones aplicadas y cuentas/horarios demo. `alembic check` no detectó cambios pendientes. Se verificaron la web, la salud de la base por el proxy de Vite, el inicio de sesión de administrador y el catálogo administrativo con respuestas HTTP 200.
- Los conflictos de Git mencionados en la revisión anterior ya estaban resueltos al comenzar esta corrección; no se crearon commits ni se modificó el índice.
- Se instalaron dependencias web con `npm ci` y backend en `.venv` con `requirements.txt`; la comprobación backend no certifica las versiones exactas de `requirements.lock`.

Para iniciar desde la raíz, ejecutar `fish iniciar.fish` o `./iniciar.fish`. El diagnóstico identifica la configuración que falte; la preparación de base y entorno está en el README principal.

## Corrección del lector y carga de cámara

El lector ya no memoriza códigos mientras está bloqueado por una confirmación. Una prueba reproduce el siguiente carné presentado durante el bloqueo y comprueba que se procese después sin retirarlo; también comprueba que mantenerlo no duplique la lectura. El lector ZXing se carga bajo demanda mediante React.lazy/Suspense desde el puesto y el carné, con indicación de carga. Los sonidos de confirmación se conservan.
