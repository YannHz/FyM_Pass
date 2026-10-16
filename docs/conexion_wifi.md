# Flutter por Wi-Fi

Para esta prueba la PC se conecta al punto de acceso Wi-Fi del teléfono. No se necesita depuración USB. La IP HTTP debe estar permitida por network_security_config.xml en Android; al cambiarla puede ser necesario recompilar e instalar el APK.

## Configuración actual en Linux

Conecta la laptop al punto de acceso **POCO F7 Pro** y ejecuta `./iniciar.sh --red auto` desde la raíz del proyecto. El lanzador detecta la IPv4 de la ruta activa en cada inicio. La IP comprobada el 12 de octubre de 2026 es `10.40.209.106`; la API responde en `http://10.40.209.106:8000/api/salud` y la web permanece en `http://127.0.0.1:5173`.

Configura Flutter con `http://10.40.209.106:8000`. Si UFW bloquea el acceso, permite solo el puerto API desde la subred actual:

```bash
sudo ufw allow in on wlan0 from 10.40.209.0/24 to 10.40.209.106 port 8000 proto tcp
```

La dirección puede cambiar al reiniciar el punto de acceso. En ese caso utiliza la nueva dirección que imprime el lanzador, actualiza el servidor móvil y adapta la regla del firewall. Falta revisar el proyecto Flutter para automatizar el descubrimiento de la laptop y verificar su permiso HTTP para esta IP.

## Verificar la conexión

1. Ejecuta `./iniciar.sh --red auto` y usa la dirección API que muestra la terminal.
2. Abre `http://IP_PC:8000/api/salud` desde el teléfono. Debe responder con `estado: disponible`.
3. En Flutter, despliega **Conexión de la demo**, introduce `http://IP_PC:8000` en **Servidor** e inicia sesión.
4. Abre el puesto QR en la PC y escanéalo desde Flutter.

Si la página de salud no abre, comprueba IP, firewall y aislamiento de clientes del punto de acceso. Mantén la terminal abierta y detén ambos servicios con Ctrl+C. Las IP de este documento corresponden a una prueba anterior y pueden cambiar.
