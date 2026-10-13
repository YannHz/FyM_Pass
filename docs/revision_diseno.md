# Administración de FyM Pass

La demo web incorpora las opciones de la referencia anterior y conserva el marcado QR conectado a la base de datos. Los datos existentes se mantienen.

| Módulo | Funcionamiento |
| --- | --- |
| Resumen | Presentes, tardanzas, faltas, solicitudes pendientes y entradas de siete días. |
| Dispositivos y puesto | Apertura y pausa, modalidades QR configurables e inventario QR/ZKTeco. ZKTeco conserva configuración; no existe conexión física implementada. |
| Asistencia diaria | Consulta por fecha, búsqueda, filtros y expediente por persona. |
| Registro manual | Carga de contingencia con hora original, responsable y motivo auditados. |
| Reportes y Excel | Consulta por periodo, filtros, paginación y exportación XLSX con los filtros aplicados. |
| Preplanilla docente | Permanencia, horas programadas, incidencias, tarifas individuales y simulación exportable. Es una estimación revisable, sin descuentos aplicados automáticamente. |
| Justificaciones | Solicitudes con sustento, referencia documental y revisión aprobada u observada. |
| Personas y carnés | Personas, cuentas, fotos, grupos, horarios, calendario, carné QR y citación imprimible. |
| Carreras y horarios | Carreras, grupos y creación de versiones de horarios con tramos semanales. |
| Tolerancias y reglas | Tolerancia por rol, anticipación, margen para ausencia, umbrales de seguimiento y días no lectivos. |

El administrador configura y revisa. El operador consulta, abre el puesto y carga registros y solicitudes; no modifica reglas, personas ni tarifas y no accede a preplanilla. Las restricciones se aplican en la API además de la interfaz.

## Revisión con apple-design

Se aplicaron principios de la skill a la web mediante HTML, React y CSS. La navegación agrupa Jornada, Gestión e Instituto; el contenido tiene jerarquía tipográfica, azul institucional, superficies neutras y colores semánticos. El tema sigue la preferencia del sistema. La pantalla de acceso, carné, puesto QR y administración comparten los tokens.

Referencias locales de la skill, leídas durante la revisión:

- `layout.md › Best practices`: jerarquía y adaptación del contenido; menú plegable en pantallas estrechas.
- `typography.md › Best practices`: fuente del sistema y jerarquía consistente.
- `color.md › Best practices`: colores por función y estados acompañados de texto.
- `accessibility.md`: etiquetas, foco visible, acceso al contenido y movimiento reducido.
- `sidebars.md › Best practices`: navegación agrupada y selección visible.
- `lists-and-tables.md › Content`: encabezados descriptivos y detalle separado en expediente.
- `entering-data.md › Best practices`: etiquetas, selectores, validación y contraseñas vacías al editar.
- `settings.md › General settings` y `Task-specific options`: reglas generales separadas de las modalidades del puesto.
- `designing-for-macos.md › Best practices` y `cross-platform.md`: principios de productividad adaptados a navegador, sin imponer controles nativos de macOS.

Se verificaron visualmente el resumen, expediente y navegación de los diez módulos, además de una pantalla de 390 × 844. Los diálogos permiten cerrar con Escape y las pestañas de expediente responden a flechas. La confirmación de marcado conserva tres segundos.

## Validación y límites

22 pruebas de backend con base temporal y 8 pruebas de frontend: autenticación, QR, duplicados, entrada/salida, auditoría, permisos, justificaciones, exportación segura y navegación con consultas pendientes. Compilación TypeScript/Vite correcta. La exportación protege las cadenas que podrían interpretarse como fórmulas de Excel.

La asistencia es de ingreso al instituto; el calendario y las citaciones no determinan asistencia a clases ni sanciones académicas. Las horas de permanencia no acreditan horas lectivas. Las carreras y grupos se crean desde el panel; no se importaron personas ficticias de la referencia. La versión Flutter no se modifica en esta entrega.

La asignación individual de horarios y tolerancias admite vigencia; cambiar el horario base de un grupo afecta consultas que dependan de ese grupo. Antes de utilizarlo con históricos institucionales, debe incorporarse vigencia de pertenencia a grupos. El resultado original de cada marcado permanece guardado.

Vite informa un paquete principal de aproximadamente 726 kB sin comprimir; se puede dividir el lector QR y módulos para optimizar carga antes de desplegar en producción.

## Estado visual actualizado

Se incorporaron superficies translúcidas, desenfoque, navegación inferior móvil con cuatro destinos, transiciones nativas con alternativa compatible y preferencias de tema/transparencia. Se respeta reducción de movimiento y se permiten superficies opacas. El control actual es un panel de preferencias, no el botón luna/sol anterior. Los estilos base y capas posteriores conviven; su consolidación está pendiente.
