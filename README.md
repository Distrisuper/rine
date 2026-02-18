# RINE Print Manager

Repositorio base para el administrador de impresión dockerizado en Raspberry Pi.

## Estructura inicial

- `docker-compose.yml`: Orquestación de servicios (API + Redis)
- `app/Dockerfile`: Imagen base para FastAPI
- `requirements.txt`: Dependencias Python
- `.env.example`: Variables de entorno

## Monitoreo de impresoras (rama `feature/cups-printer-monitoring`)

Estado de la flota vía CUPS (ready/not_ready por impresora). Para probar por interfaz:

- **Flota completa:** `GET /printers/status` — JSON con todas las impresoras y su estado.
- **Una impresora:** `GET /printers/status/{nombre}` — 404 si no existe o CUPS no disponible.

En Windows, **sin** `RINE_MOCK_PRINTERS=1`, CUPS no está disponible; la API responde con `_cups_unavailable: true` y `printers: {}`. Con el mock habilitado devuelve datos de prueba. En Linux/Raspberry con CUPS instalado se listan las impresoras reales.

**Testing:** Levantar la API (`python -m uvicorn app.main:app --reload`) y abrir la documentación interactiva: `http://127.0.0.1:8000/docs` → probar `GET /printers/status`. O con curl: `curl http://127.0.0.1:8000/printers/status`.

#### Probar en Windows (sin CUPS)

En Windows CUPS no existe. Por defecto (sin `RINE_MOCK_PRINTERS=1`) verás `_cups_unavailable: true` y `printers: {}`. Para probar la misma estructura de respuesta que en la Pi (impresoras listadas con estado):

1. Crear un `.env` en la raíz del proyecto (o exportar la variable en la consola).
2. Definir `RINE_MOCK_PRINTERS=1`.
3. Levantar la API: `uvicorn app.main:app --reload`.
4. Abrir `http://127.0.0.1:8000/docs` y probar:
   - `GET /printers/status` → verás dos impresoras de ejemplo (PC42t en ready, LaserOficina en not_ready).
   - `GET /printers/status/PC42t` → estado de la PC42t.
   - `GET /printers/status/LaserOficina` → estado de la láser.

La respuesta incluye `"_mock": true` para indicar que son datos de prueba.

En PowerShell (solo para esa sesión):
```powershell
$env:RINE_MOCK_PRINTERS="1"; python -m uvicorn app.main:app --reload
```

### Raspberry Pi: Honeywell PC42t por USB

Conexión por USB. CUPS no autodetecta: hay que agregar la impresora una vez en la Pi. Luego el monitoreo la lista en `/printers/status`.

1. Conectar la PC42t por USB a la Raspberry.
2. En la Pi, listar el URI USB (suele ser `usb://Honeywell/PC42t` o similar):
   ```bash
   lpinfo -v | grep -i usb
   ```
3. Crear la cola en CUPS (cola raw para ZPL/etiquetas):
   ```bash
   sudo lpadmin -p PC42t -E -v <URI_del_paso_2> -m raw
   ```
   Ejemplo si el URI es `usb://Honeywell/PC42t`:
   ```bash
   sudo lpadmin -p PC42t -E -v usb://Honeywell/PC42t -m raw
   ```
4. Comprobar: `lpstat -p -d` y luego `GET /printers/status` en la API; debe aparecer `PC42t` con su estado.
