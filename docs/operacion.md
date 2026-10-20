# Operación y pruebas locales

Actualizado: 19 de octubre de 2026 · 0.2.0-beta.3.

El [README](../README.md) reúne instalación y arranque. Esta guía conserva operación, datos de prueba y acceso desde teléfono.

## Cuentas y datos de beta

El conjunto inicial tiene 28 personas ficticias: 4 administrativos, 6 docentes y 18 estudiantes. Referencias: mariasalazar y jorgemendoza (administradores), rosaquispe (operadora), carlosvargas (personal administrativo), luishuaman (docente) y diegoflores (estudiante). Los roles no sustituyen los permisos.

Los usuarios no llevan puntos. Las credenciales completas están en README_CREDENCIALES.local.md y backend/.credenciales_beta.local.txt, excluidos de Git. No se recrean cuentas al arrancar. El formulario permite registrar personas sin cuenta; si se solicita acceso exige usuario y contraseña, con mínimo de seis caracteres en esta beta.

Tres carreras ilustrativas: Desarrollo de Sistemas de Información, Contabilidad y Administración de Empresas. Seis grupos de ciclo I, mañana/tarde, tres alumnos por grupo. Jornadas de lunes a viernes: administración 08–17, docentes 08–13 o 14–19, estudiantes solo ingreso 08 o 14. Los registros realizados durante pruebas se conservan; no reiniciar la base para repetir un recorrido.

## Puesto y marcado

1. Iniciar MySQL, API y web; entrar con administrador u operador.
2. Abrir Dispositivos y puesto; seleccionar QR dinámico, cámara o ambos, e iniciar asistencia. Permitir la ventana emergente.
3. Activar la cámara en el puesto si corresponde y conceder su permiso.
4. Desde la cuenta personal, presentar el carnet al lector o escanear el QR del puesto. La cámara del teléfono requiere HTTPS válido fuera de localhost.
5. Verificar la confirmación de tres segundos: nombre, iniciales, rol, movimiento, hora y resultado.
6. Al terminar, pausar desde el panel. Cerrar la ventana no pausa el puesto. Reabrir reemplaza la credencial anterior.

El QR dinámico cambia cada treinta segundos y solo acepta el bloque vigente. Ambos QR tienen firma HMAC. El puesto tiene acceso limitado por hasta dieciséis horas; su token se mantiene en sessionStorage y se retira del fragmento de URL después de abrir.

Los estudiantes registran una entrada por día local; docentes y administrativos una entrada y una salida. No hay reingresos. Repetir una lectura dentro de diez segundos devuelve el resultado existente; el UUID evita repetir la misma solicitud. Retirar el carnet de la cámara al menos 1,5 segundos antes de volver a mostrarlo.

Sin horario/tolerancia se conserva «Registrado · horario pendiente». No se evalúa salida anticipada. Esta asistencia corresponde al ingreso al instituto, no a clases ni a sanciones académicas. La preplanilla es estimada, no calcula pagos definitivos ni descuentos automáticos.

La cámara procesa imágenes en el navegador, sin enviarlas ni almacenarlas. No se cargan ni muestran fotos personales. Se usa la primera letra del primer nombre y del primer apellido para todos los roles. Los archivos históricos se conservan sin uso en la interfaz. Las pestañas del mismo perfil comparten sesión; para otras cuentas usar perfil separado o ventana privada. Para un puesto desatendido definitivo, separar el perfil de la cuenta administrativa.

Ante un fallo se distinguen carga, falta de conexión y puesto cerrado. El puesto oculta QR y deshabilita lectura si no puede consultar el servidor. No confirma localmente. Si el sistema no está disponible, se conserva el registro externo para revisión por administración; el registro manual de esta beta solo permite entradas de hoy con la hora del servidor.

## Teléfono y túnel HTTPS temporal

La PC y el teléfono necesitan internet. No es necesario compartir Wi-Fi cuando se usa el túnel. Cloudflared ya se utilizó con éxito en esta instalación. No conservar enlaces anteriores: cambian al reiniciar el túnel.

Con MySQL y API activos, en PowerShell:

```powershell
cd D:\dev_\FyM_Pass\web
npm run build
npx vite preview --host 127.0.0.1 --port 4173 --strictPort
```

En otra terminal:

```powershell
cloudflared tunnel --url http://127.0.0.1:4173 --http-host-header localhost
```

Si falta Cloudflared, instalarlo desde su proveedor oficial o mediante `winget install --id Cloudflare.cloudflared --exact`. Abrir una nueva terminal después de instalar.

Abrir en el teléfono la dirección HTTPS que imprime Cloudflared. Usar el mismo enlace en la PC para probar el puesto. El proxy de Vite Preview envía /api al backend local del puerto 8000; no se necesita un túnel separado para MySQL o la API.

El enlace expone temporalmente el acceso al sistema. Compartir solo con participantes y conservar datos ficticios. Mantener PC, servicios y túnel activos. Ctrl+C en la terminal del túnel corta ese acceso. No se inicia un túnel automáticamente al arrancar el proyecto.

Un 502 suele indicar que Preview no está disponible en 4173. Si abre la interfaz pero no inicia sesión, comprobar API y base. La ruta /api/salud/base-datos ayuda a distinguirlos. No desactivar validación de certificados ni abrir MySQL a internet.

En una red local, consultar http://IP_PC:8000/api/salud solo comprueba alcance de API. Localhost del teléfono no es la PC. El modo `./iniciar.sh --red auto` no configura HTTPS; no habilita por sí mismo cámara/PWA desde otro equipo.

## Instalación PWA y actualizaciones

La compilación registra el service worker en un contexto seguro; el servidor de desarrollo no lo registra. En iPhone usar Safari y Añadir a pantalla de inicio; Android/PC ofrecen instalación según navegador. La ayuda Instalar FyM Pass está en acceso y cuenta.

Solo se cachean recursos públicos de interfaz. No hay carnet offline ni cola de sincronización; fotos, cookies, reportes y respuestas API no se guardan en esa caché. Sin servidor se muestra contingencia.

Las actualizaciones esperan a cerrar las ventanas antiguas; no forzar recarga durante marcados. Los iconos instalados pueden requerir reinstalación según navegador. La PWA instalada desde un túnel dejará de conectar al cerrarlo o cambiar de enlace. El VPS y dominio permanentes siguen pendientes.

## Base, respaldo y preparación de datos

DBeaver: MariaDB, host 127.0.0.1, puerto 3306, base fym_pass, con la cuenta privada configurada. No publicar .env ni credenciales. Conservar CLAVE_QR para mantener validez de carnets. Base y fotos no viajan mediante Git.

Desde backend, consultar/aplicar migraciones explícitamente con el Python de su entorno: `python -m alembic current` y `python -m alembic upgrade head`. No revertir migraciones en una base que se quiera conservar.

El preparador `python -m aplicacion.datos_beta --confirmar-base fym_pass` es manual, requiere base local y mysqldump/mariadb-dump para respaldo; rechaza una nueva carga si existen personas. No ejecutarlo al arrancar.

- `--actualizar-accesos` conserva personas, carnets, grupos, horarios y registros; actualiza cuentas del conjunto ficticio, revoca sesiones y pausa puestos.
- `--reemplazar-usuarios` descarta personas y registros vinculados. Solo usar ante una solicitud explícita de reinicio; no combinar con la opción anterior.

Respaldos privados en backend/archivos/respaldos; fotos en backend/archivos/fotos. Para restaurar, detener la API y verificar primero el volcado en otra base. La restauración externa todavía requiere validación. No eliminar fotos, respaldos o datos al limpiar documentación.

## Comprobación antes de una sesión

Comprobar salud de API/base, acceso por permiso, ambas modalidades QR, duplicados, pausa, carga manual y exportación. Revisar horarios antes de evaluar puntualidad; no cambiar el reloj ni borrar registros para repetir pruebas. Compilar la web después de editar y antes de probar PWA/túnel.

No hay suites automatizadas ni Docker por decisión del usuario. Una compilación no confirma cámara física, instalación en iPhone ni concurrencia real.


## Mi espacio personal

Junto a Mi carnet se muestra Mis asistencias, sin ocultarlo dentro de Mi cuenta. Está disponible para alumnos, docentes y administrativos desde su espacio personal. Permite cambiar de mes al deslizar horizontalmente (izquierda: siguiente; derecha: anterior), mediante flechas o pulsando el título del calendario para elegir mes/año. No hay selector externo. Solo admite el mes actual o anteriores, desde enero de 2000. Muestra un calendario de lunes a domingo, con colores y símbolos para ingreso, tardanza, inasistencia y justificación. Al seleccionar un día se muestran sus horas y estado debajo del calendario. Los días futuros se muestran sin evaluar y no se pueden seleccionar. Conserva el resumen de ingresos, tardanzas e inasistencias. La salida se muestra solo para roles que la requieren. El historial utiliza las mismas reglas del panel y muestra días no programados y justificaciones; no permite editar registros. Los horarios/grupos vigentes influyen en la evaluación histórica, cuya vigencia completa sigue pendiente.

La API deriva la persona de la sesión y filtra sus consultas por esa identidad. No acepta elegir otra persona. Las respuestas no se cachean. Si detecta un error, el usuario debe contactar a administración.

El sonido de confirmación está activo sin interruptor en carnet y puesto. El navegador puede exigir una primera interacción: pulsar cualquier control o tocar la pantalla prepara el audio automáticamente. En una ventana del puesto recién abierta, tocar una vez antes de empezar si el navegador bloquea reproducción automática. Se mantienen tonos distintos para entrada, salida, repetición y rechazo. La reproducción física debe verificarse en el dispositivo; las confirmaciones visuales conservan tres segundos.


## Asistencia diaria en vivo

Asistencia diaria muestra únicamente personas con una entrada o salida en la fecha consultada, ordenadas por su último marcado (más reciente primero). Una misma persona conserva su fila con entrada y salida; no es un padrón de personas pendientes. Si no hay marcados, la jornada se muestra vacía. El bloque de jornada del Resumen también excluye a quienes no han marcado, aunque sus métricas de faltas siguen evaluando el conjunto programado.

La lista diaria recibe avisos al confirmar un marcado mediante espera HTTP larga (hasta veinte segundos sin cambios, respuesta inmediata al confirmar), conserva los filtros y evita vaciar la tabla entre consultas. No superpone peticiones. Al volver a la pestaña se consulta de nuevo; si falla la red se avisa y se recupera automáticamente cuando vuelve a responder. Al pie aparece el último marcado de la fecha consultada: persona, entrada o salida y hora, independientemente de los filtros de la tabla.

Si se está viendo la jornada actual, al cambiar el día en America/Lima la fecha avanza y se consultan sus registros desde cero, solo visualmente. No se elimina ni reinicia la base. Si se eligió una fecha histórica, se conserva esa consulta. Reportes y expedientes siguen mostrando faltas, pendientes y demás estados; el Excel de Asistencia diaria exporta solo personas con marcados, usando los filtros elegidos.

Los avisos de asistencia funcionan en memoria con un único proceso de API, incluyendo QR y registro manual después del commit. Son compatibles con el túnel HTTPS temporal. Al reconectar se recupera la tabla; si falla la conexión se reintenta cada tres segundos. Antes de usar varios procesos se requiere un canal compartido de avisos.

La barra superior administrativa muestra la fecha actual de Lima y el estado del puesto, sin repetir logo ni título de sección. Consulta el estado cada quince segundos y al abrir/pausar el puesto desde el panel; ante error indica «Estado sin confirmar». La fecha de consulta histórica sigue siendo independiente.

Los filtros de rol y estado usan menús redondeados que siguen el tema claro u oscuro. Admiten flechas, Inicio/Fin, escritura para buscar una opción y Enter para elegir; Escape, Tab o un clic fuera cierran el menú. El nombre y código de cada persona comparten un área de consulta con foco visible y espacio interior.

Las barras de desplazamiento de página, menú lateral y paneles usan una pista transparente e indicadores finos y redondeados, adaptados al tema. Permanecen visibles cuando hay contenido para desplazar; el alto contraste conserva un indicador más marcado.

El expediente conserva título y cierre fuera del área desplazable. Su barra queda dentro del contorno redondeado y el fondo de la página no se desplaza mientras está abierto. La impresión conserva todo el contenido sin recortarlo al alto de la ventana.

Las fechas de consulta y de periodo utilizan un calendario integrado con selección de mes y año, navegación por flechas, Escape y acceso a Hoy. El filtro de carreras comparte el estilo de roles y estados. La denominación visible es «carnet»/«carnets»; las rutas y el formato QR mantienen sus identificadores previos para conservar compatibilidad.

Mis asistencias presenta únicamente «Consulta tus registros de asistencia» como introducción, sin botón de actualización manual. Conserva los contadores, el calendario y la renovación de datos al cambiar de mes o recuperar la sesión.

Mi carnet conserva solo la descripción sobre el escaneo. La tarjeta personal empieza por las iniciales, nombre, rol y código, seguida del QR; no repite el logo, el nombre de la aplicación ni la sede del encabezado general.

## Registro manual presencial

Registro manual permite buscar estudiantes activos por nombre, apellido o código, sin necesidad de que tengan cuenta o teléfono. Los resultados muestran código, grupo y estado de ingreso de hoy. Al seleccionar una persona se muestra su ficha y la acción Registrar entrada. No se solicitan fecha, hora ni motivo: el servidor fija la hora actual, el movimiento de entrada y la descripción auditada, conservando al responsable.

Solo administradores y operadores pueden registrar. La API rechaza estudiantes desactivados, personas de otra sede, roles distintos a estudiante, entradas duplicadas y cambios de fecha/hora o tipo de movimiento enviados por el cliente. Una persona en Falta o Justificado sin entrada debe acudir a administración; no se regulariza desde este flujo. Se respetan la tolerancia y el plazo de falta configurados, además de la anticipación cuando existe. No hay cargas retroactivas ni salidas manuales en esta sección.

Una confirmación muestra nombre, hora y resultado y devuelve el foco al buscador. El UUID se conserva para reintentar una solicitud cuyo resultado no se pudo confirmar. Debajo aparecen las entradas manuales de hoy con responsable y resultado. La búsqueda no depende de que la persona ya tenga marcados.

Los registros se guardan en la misma tabla de marcados que los QR. El aviso posterior al commit actualiza Asistencia diaria y también el Resumen: presentes, tardanzas, faltas, jornada y gráfico de los últimos siete días. Otros paneles abiertos reciben los avisos con el mismo mecanismo existente de un proceso de API. Al cambiar el día en Lima se consulta la nueva jornada sin eliminar registros.
