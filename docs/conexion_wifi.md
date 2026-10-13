# Flutter por Wi-Fi

Para esta prueba la PC se conecta al punto de acceso Wi-Fi del teléfono. No se necesita depuración USB. La IP HTTP debe estar permitida por network_security_config.xml en Android; al cambiarla puede ser necesario recompilar e instalar el APK.

## Configuración actual en Linux

Conecta la laptop al punto de acceso **POCO F7 Pro** y ejecuta `fish iniciar_hotspot.fish` desde la raíz del proyecto. El lanzador detecta la IPv4 de la ruta activa en cada inicio. La IP comprobada el 12 de octubre de 2026 es `10.40.209.106`; la API responde en `http://10.40.209.106:8000/api/salud` y la web permanece en `http://127.0.0.1:5173`.

Configura Flutter con `http://10.40.209.106:8000`. Si UFW bloquea el acceso, permite solo el puerto API desde la subred actual:

```fish
sudo ufw allow in on wlan0 from 10.40.209.0/24 to 10.40.209.106 port 8000 proto tcp
```

La dirección puede cambiar al reiniciar el punto de acceso. En ese caso utiliza la nueva dirección que imprime el lanzador, actualiza el servidor móvil y adapta la regla del firewall. Falta revisar el proyecto Flutter para automatizar el descubrimiento de la laptop y verificar su permiso HTTP para esta IP.

## Prueba anterior en Windows

1. Mantener activo el punto de acceso del teléfono y conectar la PC a ese Wi-Fi.
2. La IP detectada inicialmente es `10.222.229.36`. Puede cambiar al reconectar; comprobarla con `ipconfig`, en el adaptador Wi-Fi.
3. Iniciar desde `D:\dev_\FyM_Pass` con `python iniciar.py --red 10.222.229.36`. Si ya hay procesos del modo local, cerrarlos antes de cambiar de modo; reiniciar también Vite para actualizar su proxy.
4. Autorizar el puerto de la API desde PowerShell como administrador: `powershell -File D:\dev_\FyM_Pass\habilitar_red.ps1 -Direccion 10.222.229.36`. La regla permite exclusivamente TCP 8000, IP del Wi-Fi y subred local. No abre MySQL ni el frontend a la red.
5. En el navegador del teléfono, abrir `http://10.222.229.36:8000/api/salud`. Debe responder con `estado: disponible`.
6. En FyM Pass móvil, cerrar sesión si todavía utiliza la conexión USB. En el acceso, desplegar **Conexión de la demo**, introducir `http://10.222.229.36:8000` en **Servidor** e iniciar sesión normalmente. La dirección se guarda al completar el acceso.
7. Abrir el puesto QR en el navegador de la PC y escanearlo desde Flutter. El registro llegará a la misma base de datos.

Para quitar la regla, ejecutar como administrador: `Remove-NetFirewallRule -DisplayName 'FyM Pass API Wi-Fi demo'`.

Si la página de salud no abre desde el teléfono, comprobar IP, firewall y aislamiento de clientes del punto de acceso. El sistema necesita que la PC esté encendida. Esta conexión HTTP es para la demo en la red local; no publicar el puerto en internet. El uso posterior con datos móviles fuera de esa red necesita un servidor accesible con HTTPS.

En Linux con fish, inicia con fish iniciar.fish --red IP_PC. Mantén la terminal abierta y detén ambos servicios con Ctrl+C. Configura el firewall según tu distribución; habilitar_red.ps1 es únicamente para Windows. Las IP de este documento corresponden a la prueba anterior y pueden cambiar.
