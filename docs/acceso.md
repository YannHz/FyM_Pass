# Acceso inicial

No existe selector de rol. El servidor obtiene rol y permisos desde la base de datos.

| Cuenta ficticia | Rol | Permiso | Destino |
| --- | --- | --- | --- |
| admin.demo | Administrativo | Administrador | /administracion |
| operador.demo | Administrativo | Operador | /operacion |
| docente.demo | Docente | Personal | /mi-acceso |
| estudiante.demo | Estudiante | Personal | /mi-acceso |

Las contraseñas generadas se encuentran únicamente en `backend/.credenciales_demo.local.txt`, excluido del repositorio. Las cuentas no se recrean ni se sobrescriben al reiniciar. No hay usuarios reales.

La contraseña se almacena como scrypt con sal aleatoria. La sesión usa un token aleatorio en una cookie HttpOnly, SameSite Strict y con duración de ocho horas. En la base solo se guarda el resumen SHA-256 del token. El cierre de sesión revoca ese token. Las cuentas desactivadas no pueden reutilizar sesiones; cada consulta verifica el estado de persona, usuario y sede.

Las operaciones POST exigen un encabezado propio y no se habilita CORS para otros orígenes. Para HTTPS define COOKIE_SEGURA=true en .env. El desarrollo local usa HTTP y cookie no Secure. El cliente no guarda tokens ni permisos en localStorage. El panel exige permiso de operador o administrador en el backend.

El límite inicial es diez intentos por minuto y dirección, en memoria del proceso. No es compartido entre procesos y se reinicia con el servidor; un despliegue público requerirá definir el proxy y el control compartido de intentos. Flutter está implementado: transporta la sesión mediante Cookie y conserva el token en flutter_secure_storage. Comparte cuentas con la web.

El panel muestra conteos reales de personas activas de la sede. El puesto QR y el carné web ya están disponibles; consulta puesto_asistencia.md. Aún no incluye gestión de usuarios ni recuperación de contraseña.
