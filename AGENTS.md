# Convenciones de FyM Pass

- Stack: React con TypeScript, FastAPI con Python, MySQL/MariaDB. Todo el acceso es web instalable (PWA); Flutter queda descartado por decisión del 18/10/2026. Producción prevista en VPS con HTTPS, desarrollo local conservado.
- Usar nombres en espanol sin tildes para archivos, carpetas, funciones, clases, variables y campos propios del proyecto.
- Conservar nombres obligatorios y habituales de archivos tecnicos: main.py, main.tsx, App.tsx, index.css, config.py, database.py, models.py, package.json, vite.config.ts y equivalentes. Los nombres propios de funciones, variables y componentes del sistema permanecen en espanol.
- Escribir comentarios solo cuando expliquen una decision esencial. El texto debe comenzar con un espacio despues del delimitador, estar en minusculas y no tener tildes. Ejemplo: `# evita marcados duplicados`.
- Mantener textos de interfaz y documentacion en espanol con ortografia normal.
- Para el diseno y revision de interfaces, seguir C:/Users/yann_/.codex/skills/apple-design/SKILL.md y leer las referencias pertinentes antes de aplicar sus recomendaciones.
- Etapa vigente: version 1.0.0, primera version funcional con ejecucion local y datos ficticios conservados. No es demo ni beta. No desplegar en el VPS por ahora.
- Alcance inicial: sede principal, estudiantes con entrada, docentes y administrativos con entrada y salida, ambas modalidades QR configurables, tolerancia por rol y carga manual auditada.
- Incorporar los modulos administrativos de D:/dev_/sistema_asistencia_fym segun la ampliacion autorizada: personas, carreras y horarios, diario, manual, reportes, justificaciones, preplanilla estimada, dispositivos y reglas. Operar con QR; la integracion fisica ZKTeco no esta solicitada. Mantener el ingreso al instituto separado de asistencia a clases y no inferir sanciones academicas.
- No guardar credenciales en el repositorio.

- Por decisión del usuario, el repositorio no incluye pruebas automatizadas ni configuración Docker; no recrearlas sin solicitud.
- Las cuentas ficticias locales usan usuario sin puntos y contraseña con primer nombre sin tildes en minúsculas + fym. Mantener credenciales completas fuera de Git.

- Documentacion unica de uso, instalacion y arquitectura: README.md. Mantener CONTEXTO_PROYECTO.md aparte para el agente y AGENTS.md para convenciones. Actualizar esos archivos antes de crear guias nuevas que dupliquen informacion.

- Usar WebP para fotografias e imagenes rasterizadas nuevas; conservar SVG para logos, iconos y QR vectoriales, y PNG para compatibilidad de iconos de instalacion PWA/Apple. No convertir vectores a mapas de bits ni modificar dependencias o respaldos para aplicar esta regla. Las nuevas fotos procesadas por el backend se guardan en WebP; conservar las rutas historicas existentes.
