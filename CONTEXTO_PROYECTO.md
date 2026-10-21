# Contexto vigente de FyM Pass

Actualizado: 19 de octubre de 2026 · versión 0.2.0-beta.3.

## Proyecto y dirección

Sistema web de asistencia del Instituto Finney Miller. Proyecto activo: D:/dev_/FyM_Pass. La demo fue aprobada; ahora es beta funcional con datos ficticios y ejecución local. La referencia inicial D:/dev_/sistema_asistencia_fym no es el proyecto activo.

React/PWA es el único cliente para PC, Android e iPhone. Flutter se descartó; el prototipo externo D:/dev_/FyM_Pass_Movil se conserva sin continuar. Administración desea alojamiento en línea; se evaluaron VPS de Hostinger/Contabo, pero no hay proveedor ni dominio contratado. El túnel HTTPS temporal de Cloudflare ya se utilizó para acceder desde teléfono. No equivale al despliegue permanente y no se inicia automáticamente.

## Dónde está la información

- README.md: descripción, tecnologías, estructura, preparación y arranque.
- docs/arquitectura.md: capas, responsabilidades, tablas y seguridad.
- docs/operacion.md: usuarios ficticios, puesto QR, PWA, túnel y recuperación de datos.
- AGENTS.md: convenciones obligatorias del repositorio.
- Este contexto: decisiones actuales, apariencia y siguientes pasos.

Las guías anteriores y README.me se consolidaron en estos documentos para evitar instrucciones duplicadas. No recrear un documento por cada ajuste visual.

## Tecnología y código

React 19, TypeScript, Vite, Tailwind, Lucide, QRCode y ZXing. API FastAPI con Python, SQLAlchemy/PyMySQL, Alembic; MySQL/MariaDB (XAMPP local). openpyxl para Excel y Pillow para fotos.

Monolito modular por capas: acceso, asistencia, gestion y diagnostico. Rutas HTTP y esquemas de validación → servicios con reglas → repositorios con SQL/transacciones. Modelo ORM e infraestructura compartidos; no es arquitectura hexagonal ni microservicios. Mantener SQL fuera de rutas y servicios de API. Migración vigente 0004.

App.tsx coordina acceso y recuperación de sesión. PanelAdministrativo.tsx compone módulos; FormularioGestion.tsx contiene formularios y editor de tramos; componentesGestion.tsx reúne consultas, tablas, estados y diálogos. servicio.ts centraliza peticiones, tiempo de espera, errores por campo y caducidad. CarneVirtual y PuestoAsistencia son pantallas separadas. Backend/aplicacion/version.py comparte versión entre API/salud y listado privado generado; web/src/version.ts identifica la versión mostrada en el login.

## Alcance funcional

Sede principal; tres sedes como ampliación futura. Estudiantes registran entrada al instituto; docentes y administrativos entrada/salida. No confundir con asistencia a clases ni deducir sanciones académicas. Permisos administrador, operador y personal distintos del rol institucional.

QR dinámico del puesto y lectura del carnet con cámara, habilitables por separado. Rotación cada treinta segundos; confirmación de tres segundos con nombre, iniciales, rol, movimiento, hora y resultado. Validación de firma, sede, horario, persona y duplicados; UUID de evento. Hora del servidor, eventos UTC y presentación Lima. Sin reingresos ni jornadas nocturnas.

Administración incluye resumen, dispositivos/puesto, diario, carga manual auditada, Excel, preplanilla estimada, justificaciones, personas/carnets/expediente/citación, carreras/grupos/horarios y reglas/calendario. ZKTeco solo inventario; no hay integración física. Preplanilla no determina pagos ni descuentos automáticos. El carnet, escaneo e historial personal están implementados. Mis asistencias es visible junto a Mi carnet; calendario mensual de lunes a domingo con resumen y símbolos/colores de estado, deslizamiento horizontal y flechas para cambiar de mes, selector de mes/año integrado al pulsar su título (sin control externo), selección de día para detalle, fechas futuras deshabilitadas, salida solo por rol y sin edición. La API /api/mi-asistencia deriva la persona de la sesión y filtra en SQL por ella, sin permitir elegir otra identidad; reutiliza reglas del diario.

Ante caída se utiliza registro manual externo con carga posterior auditada. La PWA solo cachea recursos públicos, sin carnets/fotos/API ni cola de sincronización offline. Instalación/cámara desde teléfonos necesita HTTPS. No iniciar el preparador de datos ni reiniciar la base para cambios visuales.

## Datos y archivos privados

El conjunto inicial tiene 28 personas ficticias, tres carreras y seis grupos, con horarios de lunes a viernes. La base puede contener marcados reales de las pruebas: conservarlos. No afirmar que sigue vacía ni generar asistencias ficticias.

Los usuarios no tienen puntos; las claves locales siguen la convención explícita del usuario en AGENTS.md. Listado privado en README_CREDENCIALES.local.md y backend/.credenciales_beta.local.txt; conexión y firma en backend/.env. No imprimir ni publicar secretos. Conservar CLAVE_QR para validez de carnets.

aplicacion.datos_beta es una herramienta manual con base local, confirmación del nombre y respaldo obligatorio. --actualizar-accesos conserva registros pero revoca sesiones y pausa puestos. --reemplazar-usuarios es destructivo; requiere solicitud explícita. No combinar ambas opciones.

.gitignore excluye entornos, dependencias, dist, logs, credenciales, base, fotos y respaldos. Esos datos no se transportan con git pull/clone. Preservar backend/archivos y configuración privada en cualquier limpieza.

## Diseño aprobado

Aplicar apple-design según AGENTS.md. Nombres propios de código en español sin tildes; archivos técnicos habituales mantienen su nombre. Comentarios solo esenciales, simples, en minúsculas y sin tildes.

Azul institucional #003397 en claro. Logo oscuro #3B82F6, controles oscuros #4F8BFF y logo sobre bandas azules #E3EDFF. Superficies con vidrio/transparencias, modo claro/oscuro por luna/sol, preferencia persistente y sincronizada. Se respetan movimiento y transparencia reducidos. Las barras laterales y superior conservan sus superficies oscuras originales: la variante azul noche fue rechazada y revertida.

SVG original en web/public/iconos/logo-institucional.svg. LogoInstitucional.tsx utiliza máscara CSS para mantener transparencia y adaptar color sin alterar el SVG. El tamaño del escudo se aumentó; mantenerlo. Acceso directo: escudo #3B82F6 sobre #0B1220, sin texto. PNG normales 180/192/512 y maskable 512 con margen; favicon SVG adaptable al tema del sistema. Los iconos instalados pueden necesitar reinstalación tras actualizar.

Estado actual del login: «Tu ingreso a / Finney y Miller.», etiqueta ISTP FINNEY & MILLER y descripción «El sistema de asistencia para estudiantes, docentes y personal administrativo.» seguida por salto de línea y «Usa tu carnet virtual y revisa tus registros.». Sin pie de sede/versión; instalador debajo de la ayuda de cuenta. En PC horizontal y vertical conservar dos columnas y alineación izquierda de textos: marca arriba, bloque de presentación y formulario centrados verticalmente. La presentación utiliza tres filas de grid (espacio flexible, contenido, espacio flexible), con la marca anclada arriba fuera del flujo, para conservar su posición al quitar el pie; no apilar columnas por orientación ni centrar el texto del formulario. En anchos de hasta 800 px se mantiene la disposición móvil.

Carnet prioriza escaneo y QR, con navegación visible hacia Mis asistencias. Sonido siempre activo sin controles de activar/silenciar, preparado mediante primera interacción con el navegador. Cabecera administrativa compacta, icono de tema visible, navegación con historial. Formularios por rol, cuenta opcional, errores asociados y editor completo de tramos sin inventar salidas. Recuperación de sesión conserva borradores y no repite escrituras automáticamente. Distinguir carga, vacío, error de red y puesto cerrado. Exportación bloquea envíos repetidos. La carga de fotos está retirada de UI/API y todas las identidades muestran iniciales del primer nombre y primer apellido (Diego Alejandro Flores Quispe → DF), calculadas en compartido/identidad.py. No borrar fotos históricas ni cambiar la base para retirar esta función.

## Arranque y verificación

iniciar.sh sigue como único lanzador de Linux, ejecutable desde fish con ./iniciar.sh, no con fish iniciar.sh. Requiere Bash, Python y MySQL activo. Opciones --red auto/IP y --sin-navegador; registros en .registros. No añadir lanzadores nuevos sin solicitud. En Windows se ejecutan Uvicorn/Vite manualmente o desde herramientas de la sesión. Preview 4173 sirve la compilación para PWA/túnel; desarrollo usa 5173. Detalles en README y operación.

El 19/10 se arrancaron MySQL, API y Vite locales, con salud de API/base y HTTP web comprobados. No se abrió un túnel público en ese arranque. No se modificaron personas, horarios ni asistencias.

Las revisiones previas comprobaron compilación, sintaxis Python, acceso por permisos y cierre, copias de horarios con salida vacía, campos por rol, navegación Atrás y renovación de sesión conservando un borrador cancelado sin guardarlo. La revisión de navegador no equivale a validar cámaras físicas ni instalación en iPhone.

Por decisión del usuario no hay suites automatizadas ni Docker; no recrearlos. Ejecutar verificaciones proporcionales al cambio. Pendientes: seguir afinando login sin recuperar cambios rechazados, validación de dispositivos, producción con dominio/HTTPS, respaldo externo/restauración, concurrencia, vigencia histórica de grupos y operación entre sedes.

Verificación del espacio personal: API comprobada con alumno, docente y administrador, sin sesión y con consultas de mes inválido/futuro; solo devuelve historial propio, sin caché. Ruta antigua de carga de foto retirada. Navegador móvil 390/320 px: carnet DF, navegación a historial y Atrás correctos, sin controles de sonido ni desbordamiento. Las comprobaciones no crearon marcados; se conservaron 28 personas y se cerraron las sesiones de revisión. Sonido físico y cámara pendientes en esta revisión.


## Regla de asistencia diaria

Asistencia diaria es una jornada en vivo, no una lista del alumnado. Solo personas con entrada o salida en la fecha elegida; más recientes primero. Recibe avisos al confirmar marcados mediante espera HTTP larga, sin parpadeo ni pérdida de filtros; vuelve a consultar al recuperar foco/visibilidad. Cuando se ve el día actual, la fecha cambia automáticamente a la nueva jornada en Lima; si se eligió fecha histórica, se mantiene. No borrar marcados ni programar limpiezas de base para esa transición. Las faltas continúan en reportes, expedientes e historial personal. La tabla de jornada del Resumen también muestra solo marcados, sin alterar sus métricas generales.

La API diario y Excel admiten solo_marcados=true; los reportes mantienen el comportamiento completo por defecto. useDatos tiene un tercer argumento opcional para el intervalo y actualizadoEn. No usar el contador revision para cada sondeo, porque vacía datos y vuelve a consultar catálogos innecesariamente.

Comprobación: administrador y operador obtienen solo marcados, Excel coincide con ese criterio, una fecha sin registros devuelve vacío y un alumno recibe 403 en la API administrativa. Se verificaron consultas periódicas y estado vacío en navegador sin crear/eliminar asistencias. Cambio de medianoche implementado mediante fecha de Lima; no se cambió el reloj del sistema para comprobarlo.

Los avisos de asistencia funcionan en memoria con un único proceso de API, incluyendo QR y registro manual después del commit. Son compatibles con el túnel HTTPS temporal. Al reconectar se recupera la tabla; si falla la conexión se reintenta cada tres segundos. Antes de usar varios procesos se requiere un canal compartido de avisos.

Registro manual actualizado el 20/10: buscador de estudiantes, entrada de hoy con hora del servidor y sin motivo editable. Se eliminan cargas retroactivas y salidas de ese flujo; Falta requiere revisión por administración. Guarda en marcados y actualiza diario y resumen/gráficos mediante avisos posteriores al commit. `POST /api/gestion/manual` solo acepta persona_id e identificador_evento. Verificación transaccional en MariaDB con rollback; no se crearon archivos de pruebas.
