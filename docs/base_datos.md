# Base de datos inicial

Migración actual: 0004. La estructura inicial se creó con 0001. Motor local: MariaDB 10.4.32 de XAMPP.

| Tabla | Propósito |
| --- | --- |
| sedes | Sede asignada y zona horaria |
| roles | Estudiante, docente y administrativo; indica si requiere salida |
| personas | Identidad, código, rol y sede |
| usuarios | Cuenta, hash de contraseña y permiso de acceso |
| horarios | Agrupación de horarios por sede |
| tramos_horarios | Día y horas; lunes=0, domingo=6; admite varios tramos |
| asignaciones_horarios | Horario de una persona con fechas de vigencia |
| tolerancias_roles | Minutos por rol y vigencia |
| puntos_asistencia | Punto de ingreso y modalidades habilitadas |
| marcados | Evento de entrada/salida, modalidad, hora original y hora de carga |
| alembic_version | Control técnico de migraciones |

Las fechas y horas de eventos se almacenan en UTC; los horarios de clase o trabajo son horas locales de la sede. El backend las convierte antes de comparar. La migración incluye solo roles, sede principal y punto de ingreso. No crea usuarios ni personas ficticias, horarios o tolerancias.

Las contraseñas se guardan como hash. El identificador único de evento evita reinsertar el mismo evento; no sustituye las reglas de duplicados cercanos en el tiempo. Las validaciones de sede asignada, salida por rol, solapamientos de vigencias y permisos están implementadas en los servicios del backend. Esta estructura inicial admite únicamente turnos dentro del mismo día.

Los registros manuales exigen usuario responsable y motivo. Las correcciones con historial completo están pendientes. La migración 0003 añade foto_ruta y version_carne a personas, puestos_abiertos y eventos_puesto. Ya hay API para registrar mediante ambas modalidades QR; la carga manual dispone de API e interfaz con responsable, motivo, hora original y auditoría.

## DBeaver

Conexión MariaDB: servidor `127.0.0.1`, puerto `3306`, base `fym_pass`. Utiliza el usuario dedicado configurado; las credenciales de esta instalación están en README_CREDENCIALES.local.md, excluido de Git. La aplicación utiliza su propio usuario `fym_pass`, cuya clave está en `backend/.env`; no publiques ese archivo. Actualiza el árbol de tablas después de conectar.

## Migraciones

Desde backend: `.\.venv\Scripts\python.exe -m alembic current` muestra la revisión y `.\.venv\Scripts\python.exe -m alembic upgrade head` aplica cambios pendientes. La revisión inicial incluye reversión, que elimina sus tablas; no la ejecutes en una base con datos que quieras conservar.

La migración 0004 añade carreras, grupos, justificaciones, días no lectivos, reglas por sede, tarifas docentes, dispositivos y auditorías; añade grupo e identificador biométrico a personas y resultado original a marcados. Sesiones, puestos y eventos ya se encuentran incluidos.
