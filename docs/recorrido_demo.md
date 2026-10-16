# Recorrido de presentación de FyM Pass

## Preparación

1. Iniciar MySQL y los servidores con `./iniciar.sh`. Para el teléfono utilizar --red auto o --red IP_PC.
2. Entrar al resumen como administrador u operador. Revisar **Conexión del sistema**: API y base disponibles. La dirección Flutter se informa solo cuando la API escucha en una IPv4 privada concreta.
3. Configurar el servidor en Flutter y comprobar /api/salud desde el teléfono. Si cambia la IP HTTP de Android, revisar network_security_config.xml y recompilar. El diagnóstico web no acredita conectividad del teléfono ni permisos del firewall.
4. Utilizar exclusivamente cuentas demo. Revisar horarios y tolerancias antes de explicar puntualidad/tardanza; el QR usa la hora real del servidor. No cambiar el reloj de la PC para forzar resultados ni borrar registros para repetir la presentación.

## Presentación de cinco minutos

| Paso | Acción | Resultado que mostrar |
| --- | --- | --- |
| 1 | Ver el diagnóstico y abrir el puesto con ambas modalidades | Servicios disponibles, puesto abierto y QR dinámico |
| 2 | Marcar con estudiante desde Flutter | Identidad y resultado durante tres segundos; una entrada |
| 3 | Consultar Asistencia diaria | Hora, rol y estado guardados en la base |
| 4 | Repetir el marcado del estudiante | Aviso de marcado previo sin insertar otra entrada |
| 5 | Presentar carné de docente o administrativo en cámara | Entrada; una lectura cercana se considera repetida y no una salida |
| 6 | Mostrar salida de personal al finalizar su jornada | Entrada y salida visibles; no se permite salida de estudiante |
| 7 | Pausar el puesto e intentar escanear | Se rechaza el marcado por puesto cerrado |
| 8 | Registrar una contingencia desde Registro manual | Hora original, motivo y responsable conservados |
| 9 | Exportar Reportes y Excel | Reporte del periodo y filtros seleccionados |

Para demostrar puntualidad y tardanza en vivo, preparar horarios de personas demo acordes al momento de presentación. La salida solo debe marcarse cuando realmente corresponda al ensayo; no presentar permanencia simulada como jornada real. Los casos con tiempos controlados están cubiertos automáticamente en una base temporal.

## Verificación automatizada

Desde backend, ejecutar el Python del entorno con `-m unittest discover -s pruebas`. test_jornada.py verifica en SQLite temporal el recorrido completo: estudiante puntual, evento idempotente, rechazo de segunda entrada, personal con tardanza, repetición cercana, salida, pausa, carga manual con auditoría y exportación. No altera la base real.

Desde web, `npm test` cubre diagnóstico disponible, caída exclusiva de base, caída total, reintento y copia de dirección, además de confirmaciones, sonidos y lectura tras bloqueo. `npm run build` verifica TypeScript y compilación.

Última comprobación de este avance: 24 pruebas backend y 15 frontend correctas. El test de jornada integra API, persistencia y Excel; la lectura física de cámara y Flutter se comprueba desde los dispositivos y no se simula como una prueba física aprobada.

## Diagnóstico de conexión

El resumen verifica cada 30 segundos y mediante **Comprobar conexión**. Muestra API y MySQL/MariaDB por separado y conserva la hora de última comprobación en Lima. Cuando se detecta una base caída, la configuración de red autenticada también puede no estar disponible porque la sesión requiere base de datos.

La ruta autenticada /api/diagnostico/conexion informa la dirección de escucha del servidor sin revelar claves o configuración de MySQL. No se presenta localhost, 0.0.0.0, IP pública o IP sin red como dirección utilizable desde el móvil. El botón Copiar dirección permite llevar la URL a Flutter. Estos estados no configuran el firewall ni publican el sistema en internet.
