# Contexto y traspaso de FyM Pass

Actualizado el **16 de octubre de 2026**, zona de referencia **America/Lima**. Este documento permite continuar el proyecto desde la ThinkPad sin disponer del historial del chat. Describe decisiones aceptadas, funcionamiento actual, verificaciones y límites. No contiene contraseñas ni claves.

## 1. Punto de partida para el agente

El usuario ya tiene una demo funcional de asistencia, web y Android, y desea pulirla antes de presentarla al instituto/profesor. No se pudo presentar en la fecha inicialmente prevista. La demo fue presentada y aprobada por el personal de administración. La última tarea reorganizó el backend como monolito modular con arquitectura por capas, manteniendo el contrato de la API.

**No empezar desde cero ni reemplazar el diseño actual.** Leer AGENTS.md en cada proyecto, inspeccionar Git y comprobar la instalación de la ThinkPad antes de proponer cambios. El pull revisado incorporó 38ad631 sobre 9871255 y Git estaba limpio antes de esta actualización. Verificar siempre el estado real del clon. El usuario conserva iniciar.sh como único lanzador. Posteriormente autorizó la separación completa de rutas, reglas y persistencia del backend; está implementada en modulos/, compartido/ e infraestructura/.

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

El repositorio web ya tiene Git. En esta copia, el historial observado es 9871255 (v1.0.5) seguido de 38ad631 (fix/ arreglo de rutas). No asumir una rama activa a partir del documento: consultar Git localmente.

## 4. Preferencias de desarrollo

- Web React con Python: combinación elegida por experiencia del usuario.
- MySQL en lugar de PostgreSQL: el usuario quiere poder explicar y mantener una base que conoce.
- Flutter, no Kotlin, para la aplicación móvil.
- Archivos, funciones, clases, variables y campos propios en **español sin tildes**.
- Conservar nombres técnicos habituales: main.py, main.tsx, App.tsx, config.py, database.py, models.py, main.dart, pubspec.yaml, etc.
- Textos de interfaz y documentación en español con ortografía normal.
- Comentarios únicamente esenciales, sencillos, en minúsculas y sin tildes, con un espacio después del delimitador.
- Diseño guiado por **apple-design**, adaptado a web y Material Android. La referencia original de la skill es `https://github.com/dickwu/apple-design-skill`.
- No asumir que la ruta Windows de la skill en AGENTS.md existe en Linux. Buscar la instalación local; si se requiere instalarla, explicar ese requisito. El pull 38ad631 volvió a incluir la skill en .agents/skills/apple-design. La ruta personal Windows de AGENTS.md no es portable; en Linux comprobar la copia del repositorio o la instalación local.
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

La apariencia utiliza un botón luna/sol que alterna claro y oscuro y guarda la elección. Si todavía no hay elección, respeta el sistema; después del clic no hay selector para regresar a automático. Sincroniza controles entre ventanas y dentro de la misma página. El control manual de reducción de transparencia se eliminó; comprobar las preferencias del sistema soportadas por CSS.

**El control actual es el botón luna/sol**, restaurado en el pull 38ad631. No reintroducir el panel de preferencias anterior basándose en instrucciones históricas. El CSS conserva estilos originales más capas posteriores; consolidarlo es un pendiente, no una modificación ya aprobada.

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

Se autorizó una regla Windows persistente, limitada a Wi-Fi/IP/TCP 8000/subred local. El agente no confirmó su creación efectiva; posteriormente el usuario confirmó que salud abría desde el teléfono y la demo funcionaba. No asumir que esa regla existe en Linux. El archivo histórico habilitar_red.ps1 fue eliminado en el pull 38ad631. Configurar el firewall de Linux según distribución y red; no referenciarlo como herramienta disponible.

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

### Lanzador actual web/API

**Únicamente iniciar.sh**, por decisión explícita del usuario el 15/10/2026. No restaurar iniciar.py, iniciar.bat, iniciar_red.bat ni los lanzadores fish salvo nueva instrucción.

```fish
./iniciar.sh
./iniciar.sh --red auto
./iniciar.sh --red IP_PC --sin-navegador
```

Puede invocarse desde fish porque el script ejecutable declara Bash en su shebang; requiere Bash y Python 3. No ejecutarlo con `fish iniciar.sh` ni con `source`. Resuelve la raíz desde cualquier carpeta y usa backend/.venv/bin/python, por lo que el arranque soportado es Linux. No hay lanzador nativo Windows actualmente; es una decisión aceptada por el usuario, no un pendiente para restaurar.

El script contiene el coordinador Python: inicia API/Vite, establece FYM_API_URL, verifica MySQL, admite --red auto/IP y --sin-navegador y finaliza los grupos de procesos que creó al cerrar. La prueba real Linux no se realizó desde este entorno Windows. En esta PC todavía se pueden ejecutar pruebas usando backend/.venv/Scripts/python.exe y npm; eso no acredita el arranque de iniciar.sh.

MySQL/MariaDB debe estar activo como servicio de Linux o mediante la instalación elegida. El lanzador no lo instala ni lo arranca con privilegios. Si no responde, termina y cierra API/web. Logs en .registros/. La web usa localhost:5173 y Flutter llega a la API en el puerto 8000 y la IP privada elegida.

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

Última verificación de la reorganización: 33 pruebas backend, 18 pruebas web y compilación. No equivale a una ejecución Linux:

- **33 pruebas backend** correctas.
- **18 pruebas frontend** correctas.
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

## 16. Estado Git y transferencia

Antes de esta tarea, el pull 38ad631 estaba aplicado y Git limpio. Esta tarea modifica pruebas y documentación, sin crear commits ni hacer push. Consultar git status para conocer el trabajo pendiente: un clone solo trae lo confirmado y publicado.

La lista de archivos sin seguimiento del traspaso del 13/10 era histórica y ya no representa el estado actual. Diagnóstico, prueba de jornada y corrección de cámara estaban incorporados a la base revisada. El contexto se copia también al proyecto móvil para facilitar el traspaso; esa copia no cambia su código Flutter.

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

## 19. Cambios de la revisión del 15/10/2026

- Se acepta el lanzador Linux único iniciar.sh; se retiran recomendaciones antiguas de recuperar Windows/fish.
- Se conserva la prueba que mantiene el QR visible al vencer y solo anima cuando llega otro código. Mostrarlo no extiende su vigencia: el backend conserva la validación de expiración.
- Se recupera además la prueba de confirmaciones: identidad, avatar, rol, resultado, tres segundos exactos por persona y cola en orden. Ambas usan mocks aislados y limpieza entre casos.
- El botón de tema actual es luna/sol; el puesto tiene ajustes para altura de pantalla y dos modalidades.
- No hubo cambios funcionales de producción ni nuevas migraciones en esta tarea; se actualizaron pruebas y contexto.

## 20. Separación por capas completada el 16/10/2026

La demo fue aprobada por administración y el usuario autorizó organizar completamente el backend. La arquitectura ahora es **monolito modular con arquitectura por capas**. No son microservicios y no se promete un dominio hexagonal independiente del ORM.

- aplicacion/main.py compone rutas y manejadores; config.py, database.py y models.py conservan sus nombres técnicos.
- aplicacion/modulos/acceso, asistencia y gestion tienen rutas.py, esquemas.py, servicios.py y repositorio.py. Diagnóstico tiene rutas, servicios y repositorio porque no recibe formularios.
- compartido/dependencias.py administra sesión y permisos HTTP. compartido/errores.py define errores sin FastAPI. compartido/codigos_qr.py comparte la firma QR. compartido/repositorio.py contiene operaciones y transacciones comunes.
- infraestructura/fotos.py valida/recomprime/guarda en backend/archivos/fotos. infraestructura/reportes.py construye XLSX.
- Los archivos antiguos acceso.py, asistencia.py, gestion.py y diagnostico.py de la raíz de aplicacion se eliminaron; no importar desde esas rutas. Usar los módulos nuevos y compartido/dependencias.py.
- Servicios no importan FastAPI/SQLAlchemy ni construyen consultas; las consultas están en los repositorios. Se utilizan entidades ORM compartidas y repositorios concretos. Los scripts de preparación demo siguen siendo herramientas administrativas separadas.
- Se preservaron puntos de commit/rollback, bloqueos, firmas, cookies y contratos. No se cambiaron frontend, Flutter, modelos ni migraciones. No hace falta reconstruir el APK por esta reorganización.
- test_capas.py compara el OpenAPI completo con pruebas/contratos/openapi.json, capturado antes del cambio: 34 rutas y sus esquemas. Comprueba además límites de imports y reglas sin HTTP/base. test_integracion_capas.py cubre fotos temporales, permisos, rollback y salud/cache.
- Las pruebas que controlan la hora ahora parchean aplicacion.modulos.asistencia.servicios o gestion.servicios. No restaurar los imports antiguos para hacer pasar pruebas.
- Último resultado: 33 pruebas backend y 18 frontend; compilación web. Se comprueba Alembic contra el servicio local cuando está disponible; no inferir una ejecución en Linux a partir de estas pruebas Windows.
- Consultar docs/arquitectura.md para la estructura actual. Las descripciones previas de archivos raíz en este documento son históricas y quedan sustituidas por esta sección.
- No se hicieron commits ni push. Conservar también los cambios locales previos de pruebas/documentación del 15/10. No restaurar scripts eliminados ni modificar secretos por conveniencia.

Comprobación final de esta reorganización: alembic check contra MariaDB local no detectó cambios; GET /api/salud y /api/salud/base-datos devolvieron 200, y las rutas protegidas sin sesión devolvieron 401. Se conservan 33 pruebas backend y 18 web correctas.
