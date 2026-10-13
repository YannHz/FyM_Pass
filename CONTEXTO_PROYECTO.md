# Contexto y traspaso de FyM Pass

Actualizado el **13 de octubre de 2026**, zona de referencia **America/Lima**. Este documento permite continuar el proyecto desde la ThinkPad sin disponer del historial del chat. Describe decisiones aceptadas, funcionamiento actual, verificaciones y límites. No contiene contraseñas ni claves.

## 1. Punto de partida para el agente

El usuario ya tiene una demo funcional de asistencia, web y Android, y desea pulirla antes de presentarla al instituto/profesor. No se pudo presentar en la fecha inicialmente prevista. La última tarea completada incorporó un diagnóstico de conexión al resumen y verificó una jornada completa mediante pruebas aisladas.

**No empezar desde cero ni reemplazar el diseño actual.** Leer AGENTS.md en cada proyecto, inspeccionar Git y comprobar la instalación de la ThinkPad antes de proponer cambios. Hay trabajo reciente sin commit en la PC Windows: el clon remoto puede no incluirlo. El usuario todavía no ha autorizado un siguiente desarrollo concreto después de este traspaso.

### Orden recomendado al retomar

1. Leer este documento, AGENTS.md y los README de ambos proyectos.
2. Revisar `git status` y confirmar que el clon contiene diagnóstico, pruebas de jornada y corrección del lector.
3. Instalar dependencias y configurar MySQL/MariaDB local. No copiar el entorno virtual ni carpetas compiladas de Windows.
4. Validar credenciales locales sin mostrarlas en mensajes o commits.
5. Ejecutar pruebas y arrancar con fish; comprobar web, API y base.
6. Configurar IP/HTTP de Android si se probará Flutter desde la ThinkPad.
7. Informar hallazgos y continuar según la siguiente instrucción del usuario. No hacer commits, push, cambios destructivos o restauraciones de base por iniciativa propia.

## 2. Institución y objetivo

Nombre de la app: **FyM Pass**. Destino: Instituto de Educación Superior Técnica Finney Miller; la interfaz también utiliza «Finney & Miller».

Antes del sistema, la asistencia se llevaba informalmente, en Excel o en hojas. El personal administrativo operará el sistema. Se registra **ingreso al instituto**, no asistencia a clases. No inferir sanciones académicas, elegibilidad ni reglas MINEDU a partir de este registro.

Población: estudiantes, docentes y personal administrativo. Cada persona tiene sede y horario asignados. Se prevén tres sedes en la misma ciudad, pero **la demo opera únicamente en la sede principal**. No hay sincronización entre sedes implementada.

La PC principal estará encendida durante la jornada, desde aproximadamente 15 minutos antes de la llegada del personal. El primero del personal administrativo abre el puesto; al finalizar se pausa/cierra. Este es el flujo operativo previsto, no una automatización de encendido de la PC.

## 3. Proyectos y ubicación

| Proyecto | Ruta original Windows | Contenido |
| --- | --- | --- |
| FyM Pass web/backend | `D:\dev_\FyM_Pass` | React, API, esquema, lanzadores y documentación |
| FyM Pass móvil | `D:\dev_\FyM_Pass_Movil` | Flutter Android |
| Referencia anterior | `D:\dev_\sistema_asistencia_fym` | Demo frontend del usuario, usada como referencia |

En Linux las rutas serán las elegidas al clonar. No codificar dependencias de D: o C: en el código compartido. La carpeta `mobile/` del proyecto web solo tiene documentación: **no contiene la app Flutter**. Clonar también el proyecto móvil o acordar una reorganización con el usuario.

El repositorio web ya tiene Git. El historial observado incluye el merge `011045d` relativo a `feat/demov3` y una eliminación de la copia `.agents/skills/apple-design`. No usar esto como prueba de la rama activa de un clon: consultar Git localmente.

## 4. Preferencias de desarrollo

- Web React con Python: combinación elegida por experiencia del usuario.
- MySQL en lugar de PostgreSQL: el usuario quiere poder explicar y mantener una base que conoce.
- Flutter, no Kotlin, para la aplicación móvil.
- Archivos, funciones, clases, variables y campos propios en **español sin tildes**.
- Conservar nombres técnicos habituales: main.py, main.tsx, App.tsx, config.py, database.py, models.py, main.dart, pubspec.yaml, etc.
- Textos de interfaz y documentación en español con ortografía normal.
- Comentarios únicamente esenciales, sencillos, en minúsculas y sin tildes, con un espacio después del delimitador.
- Diseño guiado por **apple-design**, adaptado a web y Material Android. La referencia original de la skill es `https://github.com/dickwu/apple-design-skill`.
- No asumir que la ruta Windows de la skill en AGENTS.md existe en Linux. Buscar la instalación local; si se requiere instalarla, explicar ese requisito. La skill ya no está incluida como copia dentro del repositorio web.
- Preservar los cambios visuales y de código que hizo el usuario. Evitar pedir confirmación para decisiones rutinarias ya autorizadas.
- No publicar credenciales ni información real. No enviar mensajes a terceros ni publicar/desplegar sin autorización.

## 5. Tecnologías y arquitectura

**Monolito modular:** React y Flutter consumen FastAPI; solo la API accede a MySQL/MariaDB. El servidor y la base corren en la PC principal.

| Capa | Implementación |
| --- | --- |
| Web | React 19, TypeScript, Vite, Tailwind CSS y Lucide |
| QR web | qrcode.react y lector ZXing @zxing/browser |
| API | Python, FastAPI, Uvicorn y Pydantic |
| Base | MySQL/MariaDB, SQLAlchemy, PyMySQL, Alembic |
| Reportes/fotos | openpyxl y Pillow |
| Móvil | Flutter/Dart, Material 3, http, qr_flutter, mobile_scanner, flutter_secure_storage y uuid |
| Pruebas | unittest, Vitest/Testing Library y flutter test |

En Windows se utiliza **MariaDB 10.4.32 de XAMPP**, aunque la decisión de stack se denomina MySQL. El diagnóstico identifica el motor. El backend usa un usuario dedicado; no conectar Flutter directamente a la base.

Eventos almacenados en UTC; la interfaz muestra Lima. Horarios de sede son horas locales. Los turnos actuales se modelan dentro del mismo día.

## 6. Autenticación y permisos

Acceso sencillo con usuario y contraseña, sin selector de rol. La identidad contiene rol institucional y permiso de cuenta; no son conceptos intercambiables.

- Administrador: gestión completa, personas/cuentas, reglas, revisión de justificaciones y preplanilla.
- Operador: consultas y operación del puesto, carga manual y registro de solicitudes; no modifica personas/reglas/tarifas ni accede a preplanilla.
- Personal: carné y marcado propio; incluye estudiantes, docentes y administrativos sin permiso de gestión.

Los permisos se verifican en API además de ocultar acciones en la interfaz. Contraseñas con scrypt; sesiones aleatorias, tokens almacenados como hashes, cookie HttpOnly/SameSite Strict y vencimiento aproximado de ocho horas. Hay límite de intentos en memoria y validación de encabezado X-Fym-Peticion en mutaciones. Para despliegue público deben revisarse proxy, HTTPS/cookies y límites compartidos.

Cuentas demo: admin.demo, operador.demo, docente.demo y estudiante.demo. **Web y Flutter comparten cuentas y contraseñas**. Las contraseñas generadas no están en este documento.

## 7. Flujo de asistencia

### Modalidades

1. **QR dinámico del puesto:** visible en la PC, rota cada 30 segundos; Flutter o el carné web lo escanean con sesión iniciada.
2. **QR del carné virtual:** la persona lo muestra desde el teléfono y la cámara del puesto lo lee.

El encargado puede habilitar/deshabilitar cada modalidad al abrir/reabrir el puesto. La pantalla de marcado se abre en una ventana de navegador independiente. Presenta QR, cámara con marco de centrado, o ambos según configuración. La cámara se activa por interacción y no graba imágenes.

### Reglas

- Estudiantes: una entrada diaria, sin salida.
- Docentes/administrativos: entrada y salida diarias.
- Firma HMAC, versión del carné, sede, persona activa, puesto y modalidad se validan en backend.
- UUID del evento para idempotencia y control de duplicados cercanos de aproximadamente diez segundos.
- La cámara evita leer continuamente el mismo QR; normalmente exige que deje de verse más de 1,5 segundos para volver a procesarlo.
- Tolerancia ajustable por rol y vigencia; anticipación opcional y margen para considerar ausencia.
- Si falta horario/tolerancia, el marcado se conserva con resultado de horario pendiente.
- Resultado original almacenado en Marcado.resultado; una justificación o modificación de reglas no debe borrar ese resultado.

### Confirmaciones y sonido

Confirmación **de tres segundos**: foto o iniciales, nombre, rol, entrada/salida, hora y resultado. En el puesto se mantiene una cola de confirmaciones.

El usuario incorporó sonidos diferenciados de entrada, salida, repetido y rechazo. Deben activarse por interacción del navegador y pueden silenciarse. También añadió el aviso explícito «La asistencia ya fue marcada».

### Contingencias

Si no hay internet pero la red local y la PC funcionan, el sistema local puede continuar. Sin acceso al servidor, Flutter no registra asistencias pendientes offline. Ante corte de energía se usa registro manual externo y luego carga individual desde administración, conservando hora original, responsable y motivo.

La propuesta inicial de digitar el propio ID por el asistente no se implementó como modalidad autónoma. La **carga manual administrativa sí existe**.

## 8. Módulos administrativos implementados

| Módulo | Estado y alcance |
| --- | --- |
| Resumen | Indicadores, semana, accesos rápidos y diagnóstico de conexión |
| Dispositivos y puesto | Apertura/pausa y modalidades; inventario QR/ZKTeco |
| Asistencia diaria | Fecha, filtros, estado, entrada/salida y expediente |
| Registro manual | Carga auditada e historial de contingencias |
| Reportes y Excel | Periodos, filtros, paginación y XLSX con los filtros aplicados |
| Preplanilla docente | Horas programadas, permanencia, incidencias, tarifa individual y simulación exportable |
| Justificaciones | Solicitud, motivo/referencia y revisión aprobada/observada |
| Personas y carnés | Identidad, cuentas, grupos, horarios, foto, calendario, carné y citación imprimible |
| Carreras y horarios | Carreras/grupos y versiones de horarios con tramos |
| Tolerancias y reglas | Tolerancia por rol, márgenes, seguimiento y días no lectivos |

**ZKTeco es configuración/inventario solamente**; el usuario aceptó operar con QR. No hay integración física ni sincronización biométrica solicitada.

La preplanilla es una estimación revisable de permanencia, no horas lectivas certificadas ni pago automático. Los descuentos son referenciales. Las citaciones y umbrales no deciden sanciones académicas.

Las fotos se validan y recomprimen a JPEG con nombre aleatorio. Los XLSX protegen cadenas interpretables como fórmulas. La API limita consultas de diario a un rango acotado de hasta aproximadamente 62 días.

## 9. Estado visual actual

El usuario hizo ajustes sobre el diseño inicial: superficies translúcidas y desenfoque, azul/índigo, botones redondeados, navegación inferior móvil con cuatro destinos (Resumen, Jornada, Gestión e Instituto) y transiciones de vista.

La apariencia contempla claro, oscuro y sistema, con reducción de transparencia y respeto por reducción de movimiento/contraste cuando corresponde. Las preferencias se guardan localmente y se sincronizan entre ventanas.

Aunque anteriormente se pidió y se implementó un botón luna/sol, **el código actual del usuario usa un panel de preferencias de apariencia**. No revertirlo basándose en instrucciones antiguas. El CSS conserva estilos originales más capas posteriores; consolidarlo es un pendiente, no una modificación ya aprobada.

## 10. Últimas correcciones completadas

### Lector y carga inicial

Se detectó que LectorCamara memorizaba el QR de la siguiente persona durante el bloqueo por una confirmación. Si lo mantenía visible después, se descartaba como repetido.

Se corrigió comprobando el bloqueo **antes** de memorizar el código; test nuevo comprueba QR A, bloqueo, QR B durante el bloqueo y lectura de B al terminar, sin exigir retirarlo y sin duplicarlo.

CarneVirtual y PuestoAsistencia cargan LectorCamara con React.lazy/Suspense. ZXing se descarga al usar cámara, en lugar de formar parte del paquete inicial. Tras el diagnóstico, la última compilación dio aproximadamente **329 kB iniciales (101 kB gzip)** y **414 kB para el lector (109 kB gzip)**, sin la advertencia anterior de paquetes superiores a 500 kB.

El usuario también había mejorado resolución preferida 1280×720, enfoque continuo cuando existe, intervalos de lectura, vista frontal reflejada y consejos de luz/distancia.

### Diagnóstico de conexión

Componente DiagnosticoConexion en Resumen: estado separado de API y base, reintento, hora Lima y actualización cada 30 segundos. Consulta `/api/salud`, `/api/salud/base-datos` y `/api/diagnostico/conexion`.

La ruta de diagnóstico está protegida para encargados. La dirección Flutter se obtiene de la dirección de escucha ASGI: solo se muestra una IPv4 privada concreta. No anuncia localhost, 0.0.0.0, IP pública ni enlace local como dirección móvil válida. Si está en localhost, indica reiniciar con --red auto o --red IP_PC.

Hay botón Copiar dirección en modo red. El diagnóstico **no verifica el teléfono, firewall o internet**. Si la base está caída, la ruta autenticada también puede fallar porque la sesión depende de ella; la interfaz informa los estados de API/base por separado.

También se añadió un recorrido desplegable de presentación y `docs/recorrido_demo.md`. No es un botón para generar/borrar marcados falsos: son instrucciones para presentar y pruebas aisladas.

## 11. Flutter actual

Proyecto separado, versión 0.1.0+1. pubspec.yaml exige Dart `^3.13.5`; el entorno anteriormente usado fue Flutter estable 3.47.7. Instalar una versión compatible, no una versión arbitraria antigua.

Implementado: acceso, restauración de sesión, carné, almacenamiento seguro, escáner y confirmación. Material 3 con azul #0b3c68 y temas claros/oscuros. Contraseña no persistida; token, identidad, servidor y carné guardados con flutter_secure_storage.

Sin red puede mostrarse un carné descargado. Foto remota no garantizada offline; hay iniciales. Sesión vencida conserva carné pero elimina token; para escanear debe autenticarse. Cierre borra datos locales; si se cierra offline, token del servidor puede durar hasta vencer.

Endpoints móviles: acceso/iniciar, acceso/actual, carne, carne/marcar, acceso/cerrar. La lógica de asistencia pertenece al backend.

La demo se compiló en APK debug, se instaló en un teléfono Android 16 y el usuario confirmó un escaneo real y conexión Wi-Fi sin cable. Hubo siete pruebas Flutter correctas y analyze sin incidencias en ese avance; **no se repitieron durante las últimas tareas web**.

Android fija NDK 30.0.16248370; las dependencias pueden pedir otros. Kotlin incremental está desactivado para evitar conflicto de unidades D:/C: en Windows. El APK debug no es una distribución de producción. iOS no ha sido validado.

Ver detalles y resolución de problemas en el proyecto móvil: `docs/guia_proyecto.md`.

## 12. Red y diferencias Windows/ThinkPad

USB inicial: `adb reverse tcp:8000 tcp:8000`; app con http://127.0.0.1:8000. Sin reverse, localhost es el teléfono. Emulador Android: dirección habitual 10.0.2.2.

Wi-Fi confirmado: la PC se conectó al punto de acceso del teléfono. La dirección usada fue 10.222.229.36, **no permanente ni obligatoria**. En la ThinkPad detectar su IP propia.

Android permite HTTP solo para las entradas de `android/app/src/main/res/xml/network_security_config.xml`, incluida la IP previa. Si cambia la IP, actualizar esa configuración y recompilar/reinstalar, o usar HTTPS. Cambiar solo el campo Servidor puede no bastar.

La opción --red auto detecta la ruta local de salida; con VPN o varios adaptadores comprobar que sea la red correcta y utilizar --red IP_PC si no lo es. No abrir MySQL a la red ni desactivar el firewall.

Se autorizó una regla Windows persistente, limitada a Wi-Fi/IP/TCP 8000/subred local. El agente no confirmó su creación efectiva; posteriormente el usuario confirmó que salud abría desde el teléfono y la demo funcionaba. No asumir que esa regla existe en Linux. `habilitar_red.ps1` es exclusivamente Windows; configurar el firewall de Linux según distribución y red.

## 13. Instalación y arranque

Usar el README actual para preparación completa. Dependencias no se instalan automáticamente al arrancar. En Linux con fish:

```fish
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock
npm --prefix web ci
cp backend/.env.example backend/.env
```

Crear base utf8mb4 y usuario dedicado local. Editar .env con host, puerto, usuario, contraseña y CLAVE_QR aleatoria de al menos 32 caracteres. No imprimirla en logs ni compartirla. Si las versiones fijadas no son compatibles con Python/plataforma, evaluar requirements.txt y verificar la instalación; no declarar reproducibilidad del lock sin probarlo.

Desde backend, para una base nueva:

```fish
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m aplicacion.datos_demo
.venv/bin/python -m aplicacion.horarios_demo
```

No ejecutar datos_demo sobre una base importada con cuentas existentes. Los preparadores crean cuentas aleatorias y horarios ficticios, no datos institucionales reales.

### Lanzadores web/API

```fish
fish iniciar.fish
fish iniciar.fish --red auto
fish iniciar_hotspot.fish
fish iniciar.fish --red IP_PC --sin-navegador
```

Windows: iniciar.bat con los mismos argumentos. Existe iniciar.sh para Bash. Todos llaman iniciar.py, que usa el Python del venv adecuado, establece FYM_API_URL para el proxy, inicia API y Vite, verifica MySQL y mantiene la terminal abierta. Ctrl+C detiene los procesos que creó. Si hay puertos ocupados, pide cerrar la instancia anterior y no mata procesos ajenos.

MySQL/MariaDB debe estar iniciado por XAMPP o como servicio Linux. El lanzador no lo instala ni lo arranca con privilegios. Si la base no responde, el arranque termina y cierra API/web. Logs en .registros/. Durante la última revisión local se encontró XAMPP MySQL apagado y se inició con su configuración existente; no inferir que seguirá activo en otra sesión.

Web: http://127.0.0.1:5173. API: puerto 8000, localhost o IP privada elegida. La web permanece en localhost incluso en modo red; Flutter llega directamente a la API.

## 14. Base y secretos

Hay cuatro migraciones Alembic (0001 a 0004). Entidades: sedes, roles, personas, usuarios, horarios/tramos/asignaciones, tolerancias, puntos, marcados, sesiones, puestos abiertos/eventos, carreras, grupos, justificaciones, días no lectivos, reglas, tarifas docentes, dispositivos y auditoría.

Ubicaciones privadas, excluidas de Git:

- backend/.env: credenciales de base y CLAVE_QR.
- backend/.credenciales_demo.local.txt: contraseñas demo generadas.
- README_CREDENCIALES.local.md: resumen local de cuentas y conexión, en ambos proyectos.
- backend/archivos/: fotos locales.

No se transfieren automáticamente al clonar. Para conservar datos de prueba entre PCs, exportar/importar por un medio privado y acordar el procedimiento; no subir un volcado a GitHub. Conservar CLAVE_QR si se quiere conservar validez de carnés importados. No regenerar usuarios o borrar marcados por conveniencia.

Las exclusiones de Git ya se verificaron para ambos proyectos. Se conservan lockfiles, documentación y fuentes; se excluyen entornos, node_modules, build/dist, secretos, firmas Android, rutas del SDK y logs. .gitignore no elimina archivos que ya estuvieran versionados.

## 15. Verificación y límites de la evidencia

Última verificación del avance web:

- **24 pruebas backend** correctas.
- **15 pruebas frontend** correctas.
- TypeScript/Vite compilan correctamente; lector separado bajo demanda.
- Diagnóstico revisado en navegador real: API y MariaDB disponibles, modo local informado correctamente y guía desplegada.
- Diagnóstico de red probado en lógica aislada para IP privada y rechazo de direcciones inapropiadas; no se hizo una nueva prueba física Flutter en este avance.
- En verificaciones anteriores, alembic check no detectó diferencias de esquema. El diagnóstico no añadió tablas ni migraciones.

test_jornada.py usa SQLite temporal e integra puntualidad, tardanza, duplicados, salida, pausa, manual auditado y Excel. No escribe en MySQL real. Esto no constituye prueba de carga/concurrencia en MariaDB ni prueba física de cámara.

Desde backend:

```fish
.venv/bin/python -m unittest discover -s pruebas
.venv/bin/python -m alembic check
```

Los tests QR necesitan CLAVE_QR válida en el entorno de prueba; con configuración vacía pueden responder 503. Evitar modificar la clave real para arreglar pruebas.

Desde raíz web/backend:

```fish
npm --prefix web test
npm --prefix web run build
```

Desde Flutter: flutter analyze, flutter test y flutter build apk --debug. Android requiere SDK/JDK/NDK. No convertir resultados históricos en afirmaciones de una nueva ejecución aprobada.

## 16. Trabajo local que debe llegar a la ThinkPad

Al elaborar este documento, Git Windows mostraba modificaciones sin commit en:

```text
README.md
backend/aplicacion/main.py
docs/analisis_proyecto.md
web/src/CarneVirtual.tsx
web/src/LectorCamara.tsx
web/src/PanelAdministrativo.tsx
web/src/PuestoAsistencia.tsx
web/src/index.css
```

Y archivos nuevos aún sin seguimiento:

```text
backend/aplicacion/diagnostico.py
backend/pruebas/test_jornada.py
docs/recorrido_demo.md
web/src/DiagnosticoConexion.tsx
web/src/DiagnosticoConexion.test.tsx
web/src/LectorCamara.test.tsx
```

Este propio CONTEXTO_PROYECTO.md se añadió después de esa inspección. **Un git clone no traerá trabajo sin commit/push**. El usuario debe transferirlo o publicar los cambios que decida; ningún commit ni push fue realizado por el agente en las tareas recientes. Volver a comprobar el estado, pues esta lista es una fotografía del momento.

## 17. Pendientes y posibles siguientes mejoras

### Antes de producción

- HTTPS y despliegue estable; no exponer la demo HTTP públicamente.
- Copias/restauración verificadas y operación ante cortes de luz/red.
- Firma Android de distribución y proceso de actualización.
- Configuración institucional definitiva: horarios, tolerancias y roles.
- Vigencia histórica de grupos/pertenencia: cambiar horario de un grupo afecta consultas antiguas que dependan de su configuración actual. Las asignaciones individuales/tolerancias sí tienen vigencia y el resultado original del marcado se conserva.
- Operación multi-sede, sincronización y reglas de conectividad aún por diseñar.
- Pruebas de concurrencia, volumen y permisos sobre el motor real.

### Mejoras propuestas, no todas autorizadas/implementadas

- Formularios por secciones y errores junto al campo.
- Mejor presentación de reportes con sede, filtros y fecha de generación.
- Datos demo de carreras/grupos preparados con un escenario coherente.
- Consulta visible del historial de auditoría, que ya se guarda en parte.
- Revocación/renovación administrativa de carné QR usando su versión individual.
- Mensajes y configuración de conexión más claros en Flutter.
- Consolidar CSS sin perder cambios visuales del usuario.

De esa propuesta, el usuario autorizó empezar por diagnóstico y recorrido de jornada; **ambos están completados**. No interpretar la lista restante como orden de implementarla automáticamente.

## 18. Documentos que conviene consultar

Web/backend: README.md, AGENTS.md, docs/arquitectura.md, docs/base_datos.md, docs/acceso.md, docs/puesto_asistencia.md, docs/conexion_wifi.md, docs/revision_diseno.md, docs/analisis_proyecto.md y docs/recorrido_demo.md.

Flutter: README.md, AGENTS.md y docs/guia_proyecto.md. Los documentos de revisiones anteriores pueden conservar cifras históricas; para el último avance usar esta sección de verificación y volver a ejecutar pruebas en la ThinkPad.

**Meta al retomar:** reproducir y estabilizar esta demo funcional, preservar trabajo del usuario y continuar con la siguiente prioridad que él indique.
