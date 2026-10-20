# Convenciones de FyM Pass

- Stack: React con TypeScript, FastAPI con Python, MySQL/MariaDB. Todo el acceso es web instalable (PWA); Flutter queda descartado por decisión del 18/10/2026. Producción prevista en VPS con HTTPS, desarrollo local conservado.
- Usar nombres en espanol sin tildes para archivos, carpetas, funciones, clases, variables y campos propios del proyecto.
- Conservar nombres obligatorios y habituales de archivos tecnicos: main.py, main.tsx, App.tsx, index.css, config.py, database.py, models.py, package.json, vite.config.ts y equivalentes. Los nombres propios de funciones, variables y componentes del sistema permanecen en espanol.
- Escribir comentarios solo cuando expliquen una decision esencial. El texto debe comenzar con un espacio despues del delimitador, estar en minusculas y no tener tildes. Ejemplo: `# evita marcados duplicados`.
- Mantener textos de interfaz y documentacion en espanol con ortografia normal.
- Para el diseno y revision de interfaces, seguir C:/Users/yann_/.codex/skills/apple-design/SKILL.md y leer las referencias pertinentes antes de aplicar sus recomendaciones.
- Etapa vigente: beta funcional local con datos ficticios (0.2.0-beta.3), no demo. No desplegar en el VPS por ahora.
- Alcance inicial: sede principal, estudiantes con entrada, docentes y administrativos con entrada y salida, ambas modalidades QR configurables, tolerancia por rol y carga manual auditada.
- Incorporar los modulos administrativos de D:/dev_/sistema_asistencia_fym segun la ampliacion autorizada: personas, carreras y horarios, diario, manual, reportes, justificaciones, preplanilla estimada, dispositivos y reglas. Operar con QR; la integracion fisica ZKTeco no esta solicitada. Mantener el ingreso al instituto separado de asistencia a clases y no inferir sanciones academicas.
- No guardar credenciales en el repositorio.

- Por decisión del usuario, el repositorio no incluye pruebas automatizadas ni configuración Docker; no recrearlas sin solicitud.
- Las cuentas ficticias locales usan usuario sin puntos y contraseña con primer nombre sin tildes en minúsculas + fym. Mantener credenciales completas fuera de Git.

- Documentacion esencial: README.md (inicio), docs/arquitectura.md (codigo y datos), docs/operacion.md (uso/PWA/tunel) y CONTEXTO_PROYECTO.md (decisiones y pendientes). Actualizar esos archivos antes de crear guias nuevas que dupliquen informacion.
