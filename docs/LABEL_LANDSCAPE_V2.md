# Rótulo Landscape 90 v2

Nuevo template de etiqueta ZPL, variante del landscape 90 existente
([zebra_label_landscape_90.zpl](../infrastructure/templates/labels/zebra_label_landscape_90.zpl)),
creado en la rama `feature/landscape-v2`.

## Cambios respecto al landscape 90 original

Archivo: [infrastructure/templates/labels/zebra_label_landscape_90_v2.zpl](../infrastructure/templates/labels/zebra_label_landscape_90_v2.zpl)

1. **Se quitó la "Ciudad" como línea separada.** Ahora se combina con el domicilio
   en una sola línea: `Domicilio: {{ address }} - {{ city }}`.
2. **Retiro por mostrador:** cuando `transport` llega como `"MOSTRADOR"`, el rótulo
   muestra `MOSTRADOR` en letra grande.
3. **Reparto:** cuando `transport` llega con el nombre de un transporte (ej. `"OCA"`,
   `"ANDREANI"`), el rótulo muestra ese nombre en letra grande.

Los puntos 2 y 3 se resuelven con **una sola sección del template**
(`^CF0,100,90 ^FO190,80^FD{{ transport }}^FS`), sin lógica condicional: el campo
`transport` ya trae el valor correcto ("MOSTRADOR" o el nombre del transporte)
según cómo se cree el print job, así que alcanza con imprimirlo grande y sin el
prefijo "Expreso:" que tenía el template original.

## Alta del template en la base

Se agregó la migración
[016_add_landscape_v2_label_template.py](../infrastructure/db/migrations/versions/016_add_landscape_v2_label_template.py),
que inserta el registro en la tabla `templates` (mismo patrón que la migración 015
del landscape 90 original):

```bash
docker compose run --rm app alembic upgrade head
```

Para usarlo hay que asignar ese template a un `Channel` (vía la UI de admin en
`/admin` o directamente en la tabla `channels`), igual que con cualquier otro
template.

## Simulación en PC sin impresora

Como en Windows no hay CUPS ni una Zebra física conectada, se agregó
[scripts/preview_zpl_label.py](../scripts/preview_zpl_label.py) para previsualizar
cualquier rótulo `.zpl` como imagen, sin necesidad de imprimir. Renderiza el
template con Jinja2 (mismo motor que usa la app) y convierte el ZPL resultante a
PNG usando la API pública y gratuita de [Labelary](https://labelary.com).

### Uso básico (datos de ejemplo)

```bash
python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl --out preview.png
```

### Con datos custom desde archivo JSON (recomendado, especialmente en PowerShell)

Pasar JSON inline como argumento (`--data '{"...": "..."}'`) puede fallar en
PowerShell: al tener comillas dobles anidadas, PowerShell trocea el argumento por
los espacios al pasarlo a un ejecutable nativo (`python.exe`), aunque esté todo
entre comillas simples. Para evitarlo, usar `--data-file` con un archivo JSON:

`scripts/example_label_data.json`:
```json
{
  "to": "Juan Perez",
  "address": "Calle Falsa 123",
  "city": "Mar del Plata",
  "packages": "2",
  "transport": "OCA"
}
```

```bash
python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl \
  --data-file scripts/example_label_data.json \
  --out preview.png
```

### Con datos custom inline (funciona en bash/cmd; evitar en PowerShell)

```bash
python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl \
  --data '{"to": "Juan Perez", "address": "Calle Falsa 123", "city": "Mar del Plata", "packages": "2", "transport": "MOSTRADOR"}'
```

### Probar el caso "mostrador"

```bash
python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl \
  --data '{"transport": "MOSTRADOR"}' --out preview_mostrador.png
```

### Probar el caso "reparto"

```bash
python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl \
  --data '{"transport": "ANDREANI"}' --out preview_reparto.png
```

## Pendiente / a validar

Los offsets (`^FO190,80`, `^FO330,80`) y el tamaño de fuente (`CF0,100,90`) de la
sección de transporte/mostrador son una primera aproximación validada con la
simulación de Labelary, pero conviene confirmarlos imprimiendo en la Zebra física,
sobre todo con domicilios largos que podrían no entrar en el ancho disponible
(el template no usa `^FB` para wrap de texto).
