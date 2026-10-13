# Arquitectura actual

React y Flutter consumen una API FastAPI modular; únicamente la API accede a MySQL/MariaDB mediante SQLAlchemy. Alembic controla el esquema. El servidor principal administra una sola sede operativa; no existe sincronización entre sedes.

Módulos backend: acceso, asistencia, gestión administrativa, seguridad, configuración y persistencia. La web incluye administración, carné, puesto y preferencias visuales. Flutter incluye sesión, almacenamiento seguro, carné offline y escáner conectado.

Los permisos se verifican en backend. Las contraseñas usan scrypt y las sesiones guardan hashes de tokens; los QR llevan firma HMAC. Los eventos usan UTC y la interfaz presenta la hora de Lima. El marcado requiere llegar al servidor; internet externo no es necesario si la red local y MySQL siguen disponibles. Un corte de luz requiere contingencia manual y carga posterior auditada.

iniciar.py es compartido entre iniciar.bat e iniciar.fish. Inicia API y Vite, comprueba la conexión a la base, registra logs y detiene sus procesos con Ctrl+C. MySQL debe estar activo. El modo --red enlaza la API a una IPv4 privada específica; la web permanece en localhost.

La demo utiliza HTTP local. HTTPS, copias verificadas, despliegue Android firmado, controles de operación institucional y vigencia histórica de grupos son trabajo previo a producción. Consulta README.md para instalación y README_CREDENCIALES.local.md para secretos locales, excluidos de Git.
