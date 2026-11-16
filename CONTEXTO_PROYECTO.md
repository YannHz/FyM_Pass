# Contexto para continuar FyM Pass

Actualizado: 21 de octubre de 2026 · **versión 1.0.0, primera versión funcional**.

## Estado y ubicación

Proyecto activo: `D:/dev_/FyM_Pass`. La versión ya no es demo ni beta; sigue ejecutándose localmente y conserva personas ficticias y marcados realizados por el usuario. No sustituir ni reiniciar datos por cambiar de versión. No se ha desplegado en VPS. Administración prevé operación en línea; Hostinger/Contabo fueron evaluados, sin elección ni dominio confirmados.

`README.md` es la documentación única de instalación, uso, arquitectura y limitaciones. `AGENTS.md` conserva instrucciones para agentes. No recrear docs/ ni una guía por cada cambio. Las credenciales locales son documentos privados, no documentación pública duplicada.

La referencia `D:/dev_/sistema_asistencia_fym` no es el proyecto activo. Flutter fue descartado; el prototipo `D:/dev_/FyM_Pass_Movil` queda fuera de este repositorio. Todo el acceso es React/PWA para PC, Android e iPhone.

## Tecnología y arquitectura

React 19, TypeScript, Vite 6, Tailwind, Lucide, QRCode y ZXing. FastAPI, SQLAlchemy/PyMySQL, Alembic y MySQL/MariaDB de XAMPP. Excel con openpyxl. Migración vigente **0005**. Versiones: `web/package.json`, su lock y `backend/aplicacion/version.py`; se eliminó el version.ts sin uso.

Monolito modular por capas: `acceso`, `asistencia`, `gestion`, `diagnostico`. Rutas/esquemas → servicios → repositorios → base. SQL en repositorios, no en rutas ni servicios HTTP. Servicios coordinan transacciones y errores de aplicación; modelos ORM compartidos. No es arquitectura hexagonal ni microservicios.

`PanelAdministrativo.tsx` compone módulos; `PersonasCarnets`, `ReportesAsistencia`, `PreplanillaDocente`, `Justificaciones` y `ToleranciasReglas` contienen sus interfaces. `FormularioGestion` reutiliza formularios; `componentesGestion` reúne tablas, diálogos y `useDatos`; `servicio` centraliza solicitudes/errores/sesión. `SelectorFiltro`, `SelectorFecha`, `SelectorHora` y `usarPanelFlotante` comparten controles y superposición dentro de diálogos. `controles.css` complementa el CSS general.

## Comportamiento aprobado

- Horarios separados visualmente entre docentes y personal administrativo. Migracion 0007: tipo_personal, carrera y turno en horarios. Para docentes se pide carrera; el nombre se genera con carrera/administracion y turno. Asignacion restringida al rol del horario. Sigue una sola entrada/salida general diaria; carrera y turno organizan el horario, no generan marcados adicionales.

- Acceso actualizado: nuevas cuentas generadas por nombre y apellidos, con cambio obligatorio de clave inicial. La migracion 0006 agrega debe_cambiar_clave. El servidor restringe las sesiones pendientes a consultar identidad, cambiar clave y cerrar sesion. La base nueva y su carga inicial quedan pendientes por decision del usuario.

- Sede principal. Docentes y personal administrativo: entrada y salida. No hay reingresos ni jornadas nocturnas. Asistencia al instituto, sin inferir asistencia a clases o sanciones.
- Permisos distintos del rol: administrador, operador y personal. Inicio de sesión sin selector de rol. Sesión con cookie; no guardar tokens de cuenta en localStorage. Caducidad abre renovación de la misma cuenta y no reenvía escrituras automáticamente.
- QR dinámico y cámara del puesto habilitables por separado. Rotación cada 30 segundos, firma HMAC, bloqueo de duplicados y UUID de evento. Puesto limitado a 16 horas, token en sessionStorage. Cerrar ventana no pausa el puesto. Decisión de diseño 31/10/2026: el QR del carné es fijo a propósito porque es la identidad de la persona; solo rota el QR del puesto para impedir marcar asistencia con una foto tomada a otro. Revocar un carné perdido queda como mejora futura, sin rotación periódica.
- Confirmación de tres segundos con nombre, iniciales, rol, movimiento, hora y resultado. Verde puntual, ámbar tardanza, azul otros aceptados/repetidos y rojo rechazo. Audio siempre activo tras la interacción requerida por el navegador. Cámara centrada con video cover y visor cuadrado en teléfono.
- Solo iniciales: primera letra del primer nombre y del primer apellido. Sin carga de fotos. Se retiró el procesador de fotos y Pillow; la ruta de archivos históricos se conserva para compatibilidad. No borrar archivos históricos ni columna de datos por limpieza visual.
- Asistencia diaria solo muestra personas con marcados; orden por movimiento reciente, actualización al confirmar y cambio visual de jornada en Lima. Historial intacto. Avisos por long polling en memoria de un proceso, compatibles con Quick Tunnel; recuperación/reintento de conexión.
- Personas: tarjetas por rol, búsqueda por nombre/ID/documento/usuario, estado/cuenta, iniciales y asignación legible. Sin fecha de consulta ni duplicado de seguimiento. Nombre abre expediente; Carnet abre directamente su pestaña. Expediente con calendario, carnet y horario; sin impresión ni citación.
- Docentes y administrativos: horario laboral con entrada y salida por día, selección y confirmación con vigencia. La migración 0005 completa asignaciones heredadas sin borrar historial. No revertirla eliminando asignaciones.
- Reportes: periodos rápidos, rango hasta 62 días, resumen de registros (no personas únicas), fechas recientes, filtros por rol y expediente del intervalo. No programado oculto por defecto. Exportación respeta todos los filtros y páginas.
- Excel de asistencia: consolidado por persona, cuadrícula por mes/rol y detalle diario en Lima. Azul institucional, leyenda A/T/F/J/P y celdas neutras para días fuera del resultado. No se copió información del colegio de referencia. Preplanilla tiene su exportación independiente.
- Preplanilla: minutos/días de tardanza como principal, observaciones, detalle diario y estimación secundaria sin descuentos automáticos. Sin tarifa se muestra explícitamente; tardanza justificada no suma al total pendiente.
- Justificaciones: faltas después del límite y tardanzas llegan a una bandeja del periodo. Buscar por nombre/ID, elegir día/tipo y registrar motivo/referencia; no crear solicitudes automáticamente. Operadores registran, administradores aprueban/observan. Previene duplicados pendientes/aprobados y casos obsoletos. Se consulta con avisos de marcado y cada 30 segundos para detectar vencimientos sin escaneos.
- Reglas: edición separada de tolerancias, marcado y seguimiento. Días no lectivos con próxima fecha, búsqueda y filtro desde hoy/todas; edición del motivo conserva la fecha. Las tolerancias se aplican desde hoy y los resultados de marcados previos se mantienen.
- Mi carnet/Mis asistencias: navegación visible, calendario mensual con deslizamiento, flechas y selector mes/año integrado. Fechas futuras deshabilitadas, detalle al elegir día y salida según rol. La API deriva la persona de la sesión; no acepta otra identidad.

## Diseño

Seguir apple-design según AGENTS.md. Azul claro `#003397`; logo oscuro `#3B82F6`, controles oscuros `#4F8BFF`, logo sobre azul `#E3EDFF`. Transparencias y degradado suave, temas persistentes y preferencias de accesibilidad. No reintroducir barras azul noche rechazadas.

Logo SVG transparente mediante máscara CSS; no poner fondo blanco. Icono PWA: escudo azul sobre `#0B1220`, sin texto, PNG 180/192/512 y maskable con margen. SVG para logos/QR; WebP para imágenes rasterizadas nuevas; PNG por compatibilidad de instalación.

Login aprobado: «Tu ingreso a / Finney y Miller.», etiqueta ISTP FINNEY & MILLER, descripción del sistema y «Usa tu carnet virtual y revisa tus registros.», tarjeta «Tu ingreso, / a un escaneo.». Sin pie sede/versión; instalación centrada bajo ayuda de cuenta. PC horizontal/vertical conserva dos columnas con contenido centrado verticalmente y textos a la izquierda; móvil según ancho, no por orientación.

Hover conserva fondo/contraste del control; no aplicar una regla genérica que pinte todos los botones de azul sólido. Conservar selección de tarjetas, pestañas y calendarios. Menús flotantes no expanden formularios y se mantienen dentro de la pantalla; hora visible en 12 h con AM/PM e interna HH:mm.

## Datos privados y ejecución

Base local nueva creada el 14/11/2026 con migraciones hasta 0006. Tiene 16 personas ficticias: 4 secretarias (administrativo/operador), 2 administradoras (administrativo/administrador) y 10 docentes (docente/personal), todas con cambio de clave obligatorio. Accesos vigentes en backend/archivos/accesos_iniciales_20261114.local.md, ignorado por Git. Los listados privados anteriores son historicos. Horarios de lunes a viernes: administracion 08–17, cinco docentes 08–13 y cinco 14–19. Sin asistencias precargadas.

Conjunto inicial: personal administrativo y docentes ficticios. No inventar registros ni afirmar que la base está vacía. Credenciales completas en `README_CREDENCIALES.local.md`, `backend/.credenciales_beta.local.txt` y `.env`; no imprimirlas ni publicarlas. Mantener `CLAVE_QR`.

`aplicacion.datos_iniciales` prepara una base local explícitamente y exige respaldo. No se ejecuta al arrancar. `--actualizar-accesos` conserva personas/asistencias, revoca sesiones y pausa puestos. `--reemplazar-usuarios` es destructivo y necesita solicitud expresa. No combinar opciones. El nombre histórico del archivo privado de credenciales se conserva.

`iniciar.sh` es el único lanzador pedido: se invoca directamente desde fish, necesita Bash. Windows usa Uvicorn/Vite manual. MySQL 3306, API 8000, desarrollo 5173, Preview 4173. No duplicar procesos ni iniciar MySQL sobre otro activo. Compilar web antes de probar PWA/túnel. No iniciar un túnel salvo solicitud; URL temporal cambia al recrearlo. No registrar una URL efímera como configuración permanente.

`.registros/`, entornos, dependencias, dist, credenciales y `backend/archivos/` están ignorados. Conservar base, respaldos y archivos privados. No recorrer junctions al borrar cachés. `web/dist` es la compilación vigente que usa Preview, no un archivo de prueba. Las cachés pueden regenerarse al ejecutar.

## Pendientes reales

Aplicado el 01/11/2026 (puntos criticos de auditoria): C1 service worker con skipWaiting/claim y aviso "FyM Pass se actualizó" con recarga manual; C2 guardar_persona revoca todas las sesiones de la cuenta al cambiar clave (RepositorioGestion.revocar_sesiones); C3 config PROXY_CONFIABLE para limitar_intentos con X-Forwarded-For, middleware de encabezados de seguridad, avisos de arranque por CLAVE_QR/COOKIE_SEGURA y /api/salud/base-datos ahora exige encargado. README actualizado con estas variables. Pendiente de auditoria a futuro: indices de auditoria/justificaciones/sesiones (migracion 0006, sesiones nunca purgadas), backoff del puesto, stale-while-revalidate en useDatos.

VPS/dominio/HTTPS permanente, respaldo externo y restauración validada, múltiples sedes, recuperación de contraseñas, canal compartido de avisos/límites para varios procesos, validación de carga y dispositivos. Sin cola offline; ante caída, registro externo para revisión. El manual actual solo admite entradas de hoy con hora del servidor y rechaza faltas ya evaluadas; no prometer carga retroactiva que aún no existe.

No hay suites automatizadas ni Docker por decisión del usuario. Se verificaron compilación, flujos locales y escrituras con rollback sin datos de prueba persistidos. No confundir compilación con validación física de cámara/iOS ni de despliegue público. No hacer commit ni push sin solicitud.

Limpieza 1.0.0: la revision automatica rechazo el borrado. Se uso retirada reversible a `.registros/retirados_1_0_0/` para documentacion duplicada, fuentes obsoletas, caches propios de Python y artefactos de verificaciones. El archivo privado sigue ignorado y no forma parte de Git; no afirmar que se purgo del disco. Los respaldos SQL, datos, credenciales y archivos historicos se conservaron. La API local se arranco con -B para evitar nuevos bytecodes; otros procesos pueden regenerar caches.

Lanzador actualizado el 22/10/2026: `./iniciar.sh` compila e inicia Preview en 4173 y API en localhost:8000; `--desarrollo` usa 5173, `--sin-compilar` reutiliza dist completo y vigente, `--sin-navegador` evita apertura. `--red auto|IP` publica la web en IP privada sin exponer directamente la API. Comprueba entorno, base, revision Alembic y versiones sin migrar ni sembrar datos; termina grupos de procesos propios con Ctrl+C. Requiere Linux/macOS con Bash/Python y se invoca directamente desde fish. `.gitattributes` conserva LF. El README ya refleja este arranque e incluye la guia del tunel HTTPS de Cloudflare. No se ejecuto un arranque real bajo Linux desde este equipo Windows; se verificaron compilacion, comprobaciones y cierre con simulaciones en memoria.
