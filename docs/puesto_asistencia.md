# Puesto de asistencia y carné

1. Inicia FyM Pass con `./iniciar.sh` en Linux. Abre el navegador; el encargado inicia sesión.
2. Selecciona las modalidades en el panel y pulsa **Iniciar asistencia**. Permite la ventana emergente.
3. En la nueva ventana verás el QR dinámico, la cámara o ambas. Si elegiste cámara, pulsa **Activar cámara** y acepta el permiso.
4. El botón **Mi carné** permite presentar el QR de la propia cuenta. Para probar otras cuentas en la misma PC utiliza otro perfil de navegador o una ventana privada; las pestañas del mismo perfil comparten la sesión de usuario.
5. Tras el marcado se muestra durante tres segundos nombre, avatar (o foto si existe), rol, movimiento, hora y resultado. Las confirmaciones del puesto se encolan. La cámara no vuelve a enviar un QR mantenido frente a ella; debe retirarse por al menos 1,5 segundos.
6. El panel muestra los últimos treinta marcados y permite pausar. Reabrir reemplaza la credencial del puesto anterior y aplica las modalidades elegidas.

## Reglas de la demo

El QR del puesto cambia cada treinta segundos y solo se acepta el bloque vigente. Contiene una firma HMAC; un QR modificado no es válido. El usuario móvil debe tener sesión iniciada. El carné se firma con una versión individual, que puede cambiarse para revocarlo en una futura gestión de credenciales.

El acceso del puesto dura hasta dieciséis horas y está limitado a lectura y confirmaciones; su credencial está en sessionStorage de esa ventana. El fragmento usado al abrirla se retira de la dirección. La ventana sigue compartiendo las cookies del perfil del navegador; para un puesto desatendido en producción se deberá separar el perfil de la sesión administrativa. Cerrar la ventana no equivale a pausar: el encargado debe pulsar **Pausar puesto** en el panel.

Estudiantes: una entrada por día local. Docentes y administrativos: una entrada y una salida por día. No hay reingresos ni turnos nocturnos en esta versión. Una lectura durante los diez segundos siguientes al marcado confirmado devuelve ese resultado sin crear otro registro ni otra notificación. El identificador de evento también evita reinsertar la misma solicitud.

Las personas DEMO tienen un horario ficticio de 08:00 a 17:00 todos los días y tolerancia de diez minutos por rol, desde el 11/10/2026. Esto permite demostrar puntualidad y tardanza; no representa el reglamento del instituto. Si falta horario o tolerancia, el marcado se conserva con resultado **Registrado · horario pendiente**. La salida se confirma sin evaluación de salida anticipada.

La hora se guarda en UTC y se presenta en America/Lima. La imagen de la cámara se procesa en el navegador y no se transmite ni se almacena en el servidor. Por ahora se usa avatar de iniciales si no existe foto; no hay formulario de subida de foto.

## Acceso desde teléfono

Esta instalación sigue disponible solo en la PC local. Para probar físicamente desde un teléfono hay que preparar una dirección accesible en la red y HTTPS confiable; desde datos móviles también hace falta acceso externo. No se han publicado servicios, instalado certificados ni cambiado el firewall. Flutter y el carné disponible sin conexión se incorporarán posteriormente.

## Verificación

Backend: pruebas de acceso, firmas QR, permisos, caducidad, registro, duplicados y modalidades con base aislada. Frontend: prueba con reloj simulado que verifica tres segundos por confirmación y orden de la cola. La lectura con cámara física debe comprobarse con los dispositivos del instituto.
