# Convenciones de FyM Pass

- Stack: React con TypeScript, FastAPI con Python, MySQL/MariaDB. Todo el acceso es web instalable (PWA); Flutter queda descartado por decisión del 18/10/2026. Producción prevista en VPS con HTTPS, desarrollo local conservado.
- Usar nombres en espanol sin tildes para archivos, carpetas, funciones, clases, variables y campos propios del proyecto.
- Conservar nombres obligatorios y habituales de archivos tecnicos: main.py, main.tsx, App.tsx, index.css, config.py, database.py, models.py, package.json, vite.config.ts y equivalentes. Los nombres propios de funciones, variables y componentes del sistema permanecen en espanol.
- Escribir comentarios solo cuando expliquen una decision esencial. El texto debe comenzar con un espacio despues del delimitador, estar en minusculas y no tener tildes. Ejemplo: `# evita marcados duplicados`.
- Mantener textos de interfaz y documentacion en espanol con ortografia normal.
- Para el diseno y revision de interfaces, seguir la skill apple-design y leer las referencias pertinentes antes de aplicar sus recomendaciones.
- Etapa vigente: version 1.0.0, primera version funcional con ejecucion local y datos ficticios conservados. El piloto en AWS EC2 se prepara por solicitud del usuario.
- Alcance inicial: sede principal, docentes y administrativos con entrada y salida, ambas modalidades QR configurables, tolerancia por rol y carga manual auditada.
- Mantener los modulos administrativos de personas, horarios laborales, diario, registro manual, reportes, justificaciones, preplanilla estimada y reglas. Operar exclusivamente con QR. Mantener el ingreso al instituto separado de asistencia a clases y no inferir sanciones academicas.
- No guardar credenciales en el repositorio.

- Por decisión del usuario, el repositorio no incluye pruebas automatizadas ni configuración Docker; no recrearlas sin solicitud.
- No documentar en archivos publicos formulas de credenciales temporales ni procedimientos internos de recuperacion. Consultar NOTAS_AGENTE.local.md para las decisiones de seguridad vigentes y no publicar ese archivo.

- README.md publico: presentacion, arquitectura, estructura del backend y frontend y requisitos de uso. Mantener NOTAS_AGENTE.local.md como contexto operativo privado e ignorado por Git; AGENTS.md conserva las convenciones publicables. No incluir secretos ni detalles de despliegue en README.md.
- Esquema vigente: migraciones Alembic 0001–0011; publicar migraciones/modelos, no volcados locales. La cuenta operativa solo tiene permisos DML; usar FYM_MIGRACION=1 para Alembic despues de preparar seguridad. No ejecutar preparar, recuperar-admin ni datos_iniciales como comprobacion rutinaria.
- iniciar.sh es Bash para Linux/macOS, incluidos usuarios fish que lo ejecutan directamente; Windows conserva comandos manuales. El arranque comprueba claves y SQL sin iniciar sesion ni consultar rutas autenticadas, y no instala, migra ni genera secretos.

- Usar WebP para fotografias e imagenes rasterizadas nuevas; conservar SVG para logos, iconos y QR vectoriales, y PNG para compatibilidad de iconos de instalacion PWA/Apple. No convertir vectores a mapas de bits ni modificar dependencias o respaldos para aplicar esta regla. Las nuevas fotos procesadas por el backend se guardan en WebP; conservar las rutas historicas existentes.
