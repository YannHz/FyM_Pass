# Requisitos y reglas de base de datos de FyM Pass

Listado para la documentación del proyecto. Los requerimientos describen las funciones y condiciones de uso del sistema. Las reglas de negocio se limitan a restricciones que el esquema de MariaDB aplica mediante claves, unicidad y comprobaciones.

El acceso administrativo a la protección de cuentas y carnets exige permiso de administrador y confirmación de la contraseña actual.

## 1. Requerimientos funcionales

| Código | Requerimiento |
| --- | --- |
| RF-01 | Permitir el inicio y cierre de sesión de usuarios activos. |
| RF-02 | Exigir el cambio de la contraseña asignada en el primer ingreso. |
| RF-03 | Aplicar permisos diferenciados para personal, operador y administrador. |
| RF-04 | Mostrar el carnet QR y la asistencia propia al personal autenticado. |
| RF-05 | Abrir y pausar puestos de asistencia con modalidades QR configurables. |
| RF-06 | Permitir que varios encargados abran puestos de asistencia simultáneamente. |
| RF-07 | Registrar entradas y salidas mediante lectura del carnet QR en el puesto. |
| RF-08 | Registrar entradas y salidas mediante lectura del QR dinámico desde el móvil. |
| RF-09 | Mostrar los marcados efectuados en los puestos abiertos. |
| RF-10 | Administrar perfiles de docentes y personal administrativo, incluida su baja lógica y reactivación sin borrar el historial. |
| RF-11 | Crear, editar, asignar y retirar horarios semanales sin alterar la asistencia histórica. |
| RF-12 | Configurar tolerancias por rol y reglas de asistencia de la sede. |
| RF-13 | Consultar el resumen y el registro diario de asistencia. |
| RF-14 | Registrar manualmente una entrada del día con motivo y responsable. |
| RF-15 | Consultar incidencias y registrar justificaciones de faltas o tardanzas. |
| RF-16 | Restringir la creación y resolución de justificaciones al administrador. |
| RF-17 | Consultar el expediente de asistencia y el historial de marcados. |
| RF-18 | Generar reportes de asistencia y exportarlos a Excel. |
| RF-19 | Calcular y exportar una preplanilla docente estimada. |
| RF-20 | Administrar días no lectivos y dispositivos QR de la sede. |
| RF-21 | Permitir al administrador restablecer el acceso temporal de una cuenta activa distinta de la propia y revocar sus sesiones. |
| RF-22 | Permitir al administrador revocar y renovar el carnet QR de una persona activa. |
| RF-23 | Consultar la auditoría de seguridad por páginas y revisar alertas de rechazos QR. |


## 2. Requerimientos no funcionales

| Código | Requerimiento |
| --- | --- |
| RNF-01 | La aplicación debe funcionar desde navegadores de escritorio y móviles como PWA. |
| RNF-02 | La interfaz debe adaptarse a distintos tamaños de pantalla y mantener textos legibles. |
| RNF-03 | El acceso público debe utilizar HTTPS; las cookies de sesión deben protegerse. |
| RNF-04 | Las contraseñas deben almacenarse como hashes, sin guardar el texto original. |
| RNF-05 | La autorización debe validarse en el servidor para cada operación protegida. |
| RNF-06 | El registro de asistencia debe requerir conexión con el servidor para su validación. |
| RNF-07 | Las consultas de datos personales y de sesión deben evitar la caché compartida. |
| RNF-08 | Las operaciones sensibles deben conservar responsable y datos de auditoría. |
| RNF-09 | La base de datos debe admitir respaldos cifrados y una restauración verificable. |
| RNF-10 | El despliegue debe poder reproducirse en un servidor Linux con la configuración privada fuera del repositorio. |
| RNF-11 | El diario y los reportes deben recuperar asignaciones y tramos de horario en bloque por intervalo, sin repetir consultas por cada persona y día. |
| RNF-12 | Las acciones de protección de cuentas y carnets deben revalidar el permiso y la contraseña actual en el servidor, y registrar el responsable. |
| RNF-13 | La auditoría de seguridad debe consultar páginas acotadas sin cargar el historial completo en el navegador. |


## 3. Reglas de negocio de la base de datos

Estas reglas reflejan restricciones declaradas en el modelo de datos. Las validaciones de secuencia de marcados, permisos y cálculo de asistencia corresponden a la lógica de la aplicación.

| Código | Regla | Restricción |
| --- | --- | --- |
| RN-BD-01 | Cada sede tiene un código único. | UNIQUE en sedes.codigo |
| RN-BD-02 | Cada rol tiene un código único. | UNIQUE en roles.codigo |
| RN-BD-03 | El código de persona es único; el documento, cuando se informa, no se repite. | UNIQUE en personas.codigo y documento |
| RN-BD-04 | Cada persona referencia una sede y un rol existentes. | Claves foráneas obligatorias |
| RN-BD-05 | Una persona puede vincularse como máximo a una cuenta de usuario. | UNIQUE en usuarios.persona_id |
| RN-BD-06 | El nombre de usuario es único y el permiso pertenece a los tres valores admitidos. | UNIQUE y CHECK en usuarios |
| RN-BD-07 | El día de un tramo horario está entre 0 y 6; la salida, si existe, es posterior a la entrada. | CHECK en tramos_horarios |
| RN-BD-08 | No se repite un tramo con igual horario, día y hora de entrada. | UNIQUE compuesto |
| RN-BD-09 | La vigencia de una asignación no termina antes de empezar y no se duplica la misma asignación inicial. | CHECK y UNIQUE en asignaciones_horarios |
| RN-BD-10 | La tolerancia no es negativa; su vigencia es válida y no se repite el inicio para un rol. | CHECK y UNIQUE en tolerancias_roles |
| RN-BD-11 | Dentro de una sede no hay dos puntos de asistencia con el mismo nombre. | UNIQUE compuesto |
| RN-BD-12 | El tipo de marcado solo puede ser entrada o salida. | CHECK en marcados.tipo |
| RN-BD-13 | La modalidad de marcado solo puede ser cámara de puesto, escaneo móvil o manual. | CHECK en marcados.modalidad |
| RN-BD-14 | Todo marcado manual identifica al usuario que lo registró y contiene un motivo no vacío. | CHECK en marcados |
| RN-BD-15 | Cada marcado tiene un identificador de evento único. | UNIQUE del identificador |
| RN-BD-16 | Cada marcado referencia una persona, un punto y un rol existentes. | Claves foráneas obligatorias |
| RN-BD-17 | Cada evento de puesto tiene identificador único y puede vincularse como máximo a un marcado. | UNIQUE en eventos_puesto |
| RN-BD-18 | Cada sesión pertenece a un usuario y su hash de token es único. | Clave foránea y UNIQUE |
| RN-BD-19 | La justificación corresponde a falta o tardanza y su estado es pendiente, aprobada u observada. | CHECK en justificaciones |
| RN-BD-20 | En una sede no se duplica un día no lectivo para la misma fecha. | UNIQUE compuesto |
| RN-BD-21 | Hay como máximo un conjunto de reglas por sede; minutos y porcentajes respetan sus límites. | UNIQUE y CHECK en reglas_sedes |
| RN-BD-22 | Cada persona tiene como máximo una tarifa docente y su importe no es negativo. | UNIQUE y CHECK en tarifas_docentes |
| RN-BD-23 | El dispositivo registrado es de tipo QR y su puerto se encuentra entre 1 y 65535. | CHECK en dispositivos |
