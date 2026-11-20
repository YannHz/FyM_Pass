# Contexto para continuar FyM Pass

Actualizado: **18 de noviembre de 2026**, America/Lima. Versión funcional **1.0.0**, ejecución local.

## Punto de entrada y límites

Proyecto activo en esta computadora: `D:/dev_/FyM_Pass`. En otro equipo utilizar la ruta del clon. Leer `AGENTS.md`, este documento y `README.md`; comprobar Git antes de editar. El README es la documentación única de instalación, uso, arquitectura y base de datos. No crear guías duplicadas.

No desplegar, hacer commit/push, regenerar usuarios, restaurar una base ni crear asistencias artificiales sin solicitud. No trasladar secretos a documentación. El usuario publicará el código en GitHub; las claves y la base local están excluidas. No convertir una verificación histórica en una prueba nueva.

Flutter fue descartado. La app es React/PWA para escritorio y teléfonos. La referencia antigua y el prototipo móvil no son el proyecto activo.

Personas: DNI obligatorio al crear, exactamente ocho dígitos ASCII; validación cliente/API, unicidad SQL. ID generado en servidor DOC-DNI o ADM-DNI según rol, nunca confiar en código enviado. Al editar registros históricos sin DNI conservar ID; no migrar ni inventar DNI de prueba. Formulario muestra ID de solo lectura y explicación del permiso; docente solo personal. Formularios.css corrige fondos de diálogos y pies compartidos sin tocar la paleta de temas.

Justificaciones: por decisión del usuario, crear desde una cuenta administradora aprueba en la misma transacción y registra responsable y auditoría. Operadoras envían a revisión; no autoaprobar pendientes históricos ni permitir que el cliente elija permisos de aprobación.

Horarios: SemanaLaboral.tsx sustituye el listado por edición visual de siete días, aplicación de horas en grupo, descanso, fecha y personas en una vista. POST /api/gestion/horarios/semana guarda horario y asignaciones atómicamente, con permisos administrativos, reglas de sede/rol/fecha y conservación histórica. Desmarcar una persona significa no aplicarle los cambios, no desvincular su horario. No prometer cifrado del frontend: el navegador necesita ese código. Build sin sourcemaps y verificar_distribucion.mjs rechaza mapas y tipos privados antes de publicar.

Simplificación posterior de horarios: elegir mediante lista visible con marca activa, no desplegable mezclado con datos editables. Mostrar el nombre y turno sobre la semana; carrera/turno bajo Editar datos; personas en sección desplegable. Mostrar fecha y Guardar cambios solo al modificar o crear, sin pie flotante permanente. Conservar los temas originales y reducir explicaciones repetidas.

## Alcance vigente

- Solo docentes y personal administrativo; secretarias con permiso operador, administradoras con permiso administrador y docentes con acceso personal.
- Una entrada y una salida general al instituto por día, incluso si hay varias carreras o turnos. Sin asistencia por clase, sanciones académicas ni múltiples reingresos.
- Sede principal. Sin sincronización multisede ni cola offline de marcados.
- QR dinámico del puesto y cámara para leer el carné, habilitables por separado. Firma HMAC, rotación del puesto cada 30 s, UUID e idempotencia.
- Carné fijo hasta revocación; renovación administrativa ya implementada. La firma/rotación no prueban presencia física frente a copia o reenvío. No prometer que evitan completamente la suplantación.
- Puesto con token en sessionStorage, duración máxima 16 h. Cerrar su ventana no lo pausa.
- Confirmación de tres segundos, iniciales, nombre, rol, movimiento, hora, resultado y sonido. No hay carga actual de fotos; el acceso histórico está autenticado.
- Registro manual limitado a entradas de hoy con hora del servidor; no permite carga retroactiva ni faltas ya evaluadas.
- Reportes Excel, justificaciones y preplanilla docente estimada, sin pagos ni descuentos automáticos.
- Marcado exclusivamente QR, sin identificadores ni dispositivos ajenos a esa modalidad.

## Horarios e interfaz

Horarios separados visualmente entre Docentes y Personal administrativo. Los docentes se organizan por carrera y turno; administrativos por turno. El nombre se genera automáticamente. La carrera se guarda como texto en horarios, sin reabrir el flujo de alumnado.

Activar días y definir entrada/salida directamente; asignación posterior con fecha. “Configurar horario” sustituye a “Crear copia”. Si ya hay asignaciones, guardar crea otra versión; nunca modificar el horario histórico en sitio. Los horarios docentes heredados sin carrera deben configurarse, no asignarles carreras inventadas.

Conservar temas, contraste, selección y modificaciones visuales del usuario. Días no seleccionados neutros, seleccionados azules. Menús y selectores flotantes dentro de diálogos; horas visibles en 12 h y valores HH:mm. Aviso de actualización PWA flotante inferior, con recarga manual.

Instalación PWA: `instalacionPwa.ts` captura beforeinstallprompt desde main.tsx y conserva el evento entre montajes del menú Cuenta. El botón abre la confirmación nativa directamente; cada evento se consume una sola vez. Sin evento, mostrar ayuda adaptada al dispositivo y conservar la confirmación del navegador.

## Acceso y seguridad

- Usuario: inicial del primer nombre + primer apellido + fym, sin tildes y minúsculas. Ante coincidencia, iniciales de apellidos restantes; no añadir números por iniciativa propia.
- Clave inicial por decisión del usuario: primer nombre + inicial de cada apellido, minúsculas y sin tildes (Ana María Pérez Rojas → anapr). Vigencia 48 h, cambio obligatorio; el restablecimiento administrativo regenera esta misma fórmula. El mínimo se aplica solo a la contraseña personal: **8–256 caracteres**, confirmada, con rechazo de patrones débiles y datos personales.
- Hash Argon2id; scrypt heredado se actualiza al ingresar correctamente.
- MFA retirado por decision expresa del usuario tras la presentacion. Todos los perfiles ingresan solo con usuario y contrasena segura de 8–256 caracteres. No reintroducir autenticadores ni codigos de recuperacion.
- Sesión absoluta de ocho horas, inactividad 30 min, aviso previo y cierre de otras sesiones. Las consultas en segundo plano no cuentan como interacción.
- Límites persistentes por cuenta/IP, esperas progresivas y auditoría. No volver al contador solo en memoria.
- Cuenta → Seguridad de mi cuenta agrupa gestión propia; administradoras ven restablecimientos, revocación de carné, auditoría paginada y alertas por rechazos QR.
- Cambiar/restablecer clave revoca sesiones; la reautenticacion solicita solo la contrasena actual. Recuperación completa de administradora solo con herramienta local y verificación de identidad.
- No permitir cambios administrativos de contraseña por el formulario Personas: utilizar el acceso temporal.
- HTTP y cookie Secure quedaron fuera del cambio por solicitud explícita. No habilitarlos ni presentar su configuración actual como producción validada.

## Arquitectura y archivos

Monolito modular: acceso, asistencia, gestion, diagnostico; rutas/esquemas → servicios → repositorios → ORM. Mantener SQL en repositorios.

Backend: FastAPI, SQLAlchemy, PyMySQL, Alembic, Argon2id, cryptography, openpyxl. Frontend: React 19, TypeScript, Vite 6, Tailwind, Lucide, qrcode.react, ZXing.

Archivos clave:
- `backend/aplicacion/models.py`, `seguridad.py`, `config.py`, `database.py`.
- `modulos/acceso/rutas_seguridad.py`, `repositorio_seguridad.py`, `repositorio_proteccion.py`, `proteccion.py`.
- `compartido/dependencias.py`: permisos y restricciones de cambio de clave.
- `administrar_seguridad.py`: preparación local, cifrado, respaldos y recuperación.
- `HorariosLaborales.tsx`, `ConfiguradorIngreso.tsx`, `ConfirmarHorario.tsx`.
- `CentroSeguridad.tsx`, `CambiarClaveInicial.tsx`, `App.tsx`.
- `FormularioGestion.tsx`: formularios y entrega de acceso temporal.

## Base y datos locales

Revisión Alembic vigente: **0010**. Hay 23 tablas de aplicación más alembic_version. El README contiene el mapa completo y las diez migraciones. Migraciones/modelos son el esquema publicable; no subir un volcado de la instalación. La 0010 elimina el identificador heredado de personas y restringe dispositivos a QR, con respaldo privado previo. Conservar las migraciones históricas para actualizar bases anteriores.

Por solicitud del usuario, database/ contiene 01_crear_esquema.sql (esquema limpio 0010) y 02_datos_iniciales.sql (tres cuentas ficticias con administrador/operador/personal, punto QR, reglas y horarios). Se verificó la importación real en base aislada, retirada después; la base operativa no se reemplazó. Ambos archivos permanecen ignorados por Git y el segundo contiene accesos iniciales privados. No alterar los respaldos cifrados previos de esa carpeta. Instrucciones centralizadas en README.

0006: cambio de contraseña; 0007: carrera/turno/tipo en horarios; 0008: refuerzo de acceso y sesiones. 0009: retira columnas MFA, conservando usuarios, contrasenas y asistencias. Carreras/grupos/rol estudiantil históricos se conservan por compatibilidad sin exponer flujo de alumnado. No borrar tablas por limpieza visual.

Base local creada el 14/11/2026, migrada el 18/11. Se conservaron 16 personas ficticias: 4 secretarias, 2 administradoras y 10 docentes. Por decisión posterior del usuario se restauró la fórmula por nombre/apellidos en las 15 cuentas con cambio pendiente, renovando vigencia de 48 h y revocando sus sesiones, con respaldo cifrado previo. Se conservó la contraseña personal ya establecida de una administradora. Los nuevos usuarios y restablecimientos utilizan esa misma fórmula. No imprimir secretos.

Horarios ficticios: administración lunes–viernes 08–17, cinco docentes 08–13 y cinco 14–19. No generar marcados para demostrar indicadores.

## Secretos, copias y permisos

Todo lo siguiente es privado, no se transfiere por Git:
- backend/.env.
- backend/archivos/seguridad/clave_respaldos.key y claves historicas privadas que se conserven para respaldos.
- administracion_bd.local.json y migraciones_bd.local.json.
- Respaldos/listados .fernet, fotos y registros locales.

MariaDB escucha en localhost. La cuenta operativa tiene SELECT/INSERT/UPDATE/DELETE sobre fym_pass; la cuenta separada fym_migracion aplica Alembic con FYM_MIGRACION=1. Root protegido; phpMyAdmin local utiliza autenticación por cookie.

Los listados y volcados históricos fueron cifrados y los originales de texto retirados después de verificar la copia. Son recuperables con la clave de respaldos. No se han purgado definitivamente. Conservar claves separadas de una copia externa; no descifrarlas para “documentar” el proyecto.

La herramienta preparar es administrativa y modifica permisos SQL; no ejecutarla como comprobación rutinaria. Las claves se generan manualmente con administrar_seguridad claves y nunca se reemplazan al arrancar.

## Arranque y transferencia

iniciar.sh sigue siendo el lanzador Bash de Linux/macOS y se invoca como ./iniciar.sh desde fish. Windows mantiene comandos manuales del README; Vite debe ejecutarse con carpeta de trabajo web.

Normal: Preview 4173 y API localhost:8000. --desarrollo usa 5173 y no acepta --red. --sin-compilar verifica dist completo/vigente. --red auto|IP expone solo la web compilada. --sin-navegador evita apertura. Ctrl+C termina solo procesos propios; no detiene MySQL.

El lanzador revisa dependencias, claves de seguridad, conexión SQL y revisión de migraciones, compila y verifica la API directa y por proxy. No usa la ruta autenticada de salud de base para arrancar. No migra, instala, siembra datos ni genera claves automáticamente.

Al clonar se requiere preparar una base nueva o restaurar privadamente una existente, instalar dependencias y aportar claves. El README distingue bootstrap de migraciones posteriores y explica el listado cifrado de datos iniciales.

## Evidencia y pendientes

Verificado en Windows: compilación web, compatibilidad scrypt/Argon2id, política de ocho caracteres, acceso sin MFA, restablecimiento, permisos, inactividad y límites persistentes en bases aisladas de MariaDB. También se restauró un respaldo de 16 cuentas en una base aislada que después se retiró. Alembic check no detectó diferencias; pip check sin conflictos.

No hay suites versionadas ni Docker por decisión del usuario. No confundir comprobaciones aisladas con pruebas de carga, cámara, iOS o pentest completo. No se ha ejecutado un arranque nativo completo bajo Linux/macOS; validar allí después de transferir.

Auditoría del 18/11: Python lock y frontend de producción sin avisos conocidos; npm completo conserva GHSA-fc5q-39xc-vjpf en picomatch 4.0.7 de desarrollo, sin parche disponible en el registro consultado. No degradar Vite ni ocultar el aviso.

Pendientes: VPS/dominio/despliegue estable, copia externa y custodia, pruebas de carga y dispositivos, varios procesos para avisos de asistencia y múltiples sedes. La restauración local ya se verificó; no listarla como inexistente.

## Antes de publicar

Revisar git status, diff y archivos versionados. Excluir .env, claves, JSON locales, datos SQL, respaldos incluso cifrados, fotos, logs, entornos, node_modules y dist. .gitignore no sanea el historial; si se descubre un secreto previamente publicado, acordar rotación y retirada. No hacer commit/push por iniciativa propia.
