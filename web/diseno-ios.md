# Diseño de FyM Pass inspirado en iOS 27

El rediseño aplica la dirección visual de iOS 27 a la interfaz React. Liquid Glass se aproxima mediante CSS: no reproduce la refracción del material nativo de Apple.

## Sistema visual

- Navegación y barras: superficies translúcidas, desenfoque y contorno luminoso.
- Variante Glassmorphism solicitada: tarjetas y carné translúcidos con esquinas de 24 a 32 px. El cristal también se aplica al contenido por elección del producto; esta extensión no corresponde al uso estricto de Liquid Glass nativo.
- Acciones principales: cápsulas con azul #007AFF en modo claro y #0A84FF en oscuro, con etiqueta oscura #00152F para mantener contraste. Controles secundarios mayormente monocromos.
- Identidad: el carné institucional es el elemento protagonista. El QR conserva fondo blanco y margen de seguridad.
- Tipografía: familia del sistema, títulos grandes y unidades relativas en los estilos nuevos.
- Navegación móvil: Resumen, Jornada, Gestión e Instituto. Cada grupo expone sus módulos y conserva los permisos existentes.

## Movimiento y accesibilidad

Las entradas de contenido duran 180 a 450 ms. Los cambios de sección usan View Transitions cuando están disponibles; una nueva navegación cancela la animación anterior. Los diálogos entran y salen con movimiento vertical breve. Los gráficos crecen una vez al entrar y no animan cada actualización de datos.

`prefers-reduced-motion` desactiva las animaciones. `prefers-reduced-transparency`, contraste aumentado y la opción “Reducir transparencia” ofrecen barras opacas. La opción manual permite reducir transparencia también cuando el navegador no expone la preferencia del sistema. La apariencia automática sigue el dispositivo; se conservan las preferencias explícitas del usuario.

| Combinación | Contraste |
| --- | --- |
| Texto principal / tarjeta clara | 16,38:1 |
| Texto secundario al 80% / tarjeta clara | 5,83:1 |
| Etiqueta oscura / azul #007AFF | 4,55:1 |
| Texto principal / tarjeta oscura | 18,69:1 |
| Texto secundario al 60% / tarjeta oscura | 6,22:1 |
| Etiqueta oscura / azul #0A84FF | 5,01:1 |
| Texto verde / fondo de éxito claro | 5,92:1 |
| Texto naranja / fondo de aviso claro | 6,20:1 |
| Texto rojo / fondo de error claro | 5,73:1 |

Los cálculos WCAG componen la tarjeta al 65% sobre el fondo base del tema, y después componen el texto secundario sobre esa tarjeta. No incluyen la variación de cada píxel de los orbes ni del contenido que se desplaza bajo las barras.

## Paleta Glassmorphism

El fondo claro usa #F2F2F7 y el oscuro #000000. Las tarjetas tienen blanco al 65% en claro y #1C1C1E al 65% en oscuro; la navegación usa blanco al 50% y #111113 al 60%, respectivamente. El desenfoque es de 25 px con saturación al 180%. Los orbes estáticos combinan azul, índigo y violeta con opacidades bajas.

Los colores semánticos originales se conservan en indicadores: verde #34C759 / #30D158, naranja #FF9500 / #FF9F0A y rojo #FF3B30 / #FF453A. El índigo es #5856D6 / #5E5CE6. Las etiquetas y cifras usan variantes de contraste cuando el color original no resulta legible sobre su superficie.

Transparencia reducida, contraste aumentado y navegadores sin desenfoque muestran superficies opacas. El QR conserva fondo blanco en ambos modos. Las variables y `data-tema` siguen la nomenclatura en español del proyecto.

## Referencias

- [Actualizaciones de iOS 27](https://support.apple.com/en-mide/149076).
- [Materiales](https://developer.apple.com/design/human-interface-guidelines/materials): Liquid Glass en la capa de navegación y controles.
- [Barras de pestañas](https://developer.apple.com/design/human-interface-guidelines/tab-bars): destinos visibles, etiquetas y navegación separada de acciones.
- [Movimiento](https://developer.apple.com/design/human-interface-guidelines/motion): movimiento breve, opcional y relacionado con la interacción.
- [Accesibilidad](https://developer.apple.com/design/human-interface-guidelines/accessibility): contraste, escalado y controles cómodos.

## Verificación

Pruebas de navegación móvil, permisos del operador, preferencias persistentes, Escape, movimiento reducido y cancelación de transiciones. Las pruebas existentes del puesto QR mantienen la confirmación durante tres segundos y respetan la cola de eventos.

La compilación valida TypeScript y CSS. La inspección visual en navegador y en un iPhone real queda pendiente porque no había navegador conectado disponible durante esta sesión.