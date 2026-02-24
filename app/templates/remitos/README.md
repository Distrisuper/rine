# Templates de remito (opción 1: archivos)

El formato del PDF se define editando estos archivos.

## Archivos

- **`logo.png`** o **`logo.svg`** (opcional) — Logo de la empresa. Si colocás uno de estos archivos en esta carpeta, el remito lo muestra en la cabecera en lugar del placeholder "D". Preferí PNG con fondo transparente o SVG; altura recomendada ~50 px para que escale bien.
- **`base_remito.html`** — Estructura y contenido. Variables Jinja2:
  - `remito_id`, `client_name`, `order_number`, `address`, `city`
  - `items` (lista de dicts con `codigo`, `descripcion`, `cantidad`, `precio`, `subtotal`)
  - `total`
- **`remito.css`** — Estilos: fuentes, márgenes, tablas, colores.

## Cómo editar

1. Abrí `base_remito.html` para cambiar textos, bloques o la tabla de ítems.
2. Abrí `remito.css` para cambiar tipografía, tamaños y márgenes (incl. `@page` para tamaño A4).
3. Guardá y volvé a generar un remito (endpoint de prueba o cola); el PDF usará los cambios.

## Variantes por sucursal

Si querés un diseño distinto por template (ej. MDP vs BA), creá `templateremnooficialMDP.html`, `templateremnooficialBA.html`, etc. El renderer usa el archivo que coincida con el `template_id`; si no existe, usa `base_remito.html`.
