# RINE Print Manager

Repositorio base para el administrador de impresión dockerizado en Raspberry Pi.

## Objetivo

- `docker-compose.yml`: Orquestación de servicios (API + Redis)
- `app/Dockerfile`: Imagen base para FastAPI
- `requirements.txt`: Dependencias Python
- `.env.example`: Variables de entorno

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine (Linux).
- Docker Compose.
- Git.
- Opcional: Make (para usar comandos abreviados).

## Instalación

1) Clonar el repositorio.

```bash
git clone https://github.com/Distrisuper/rine.git
```

2) Crear el archivo de entorno a partir del ejemplo:

```bash
# Linux/macOS
cp .env.example .env
```

```bash
# Windows
copy .env.example .env
```

3) Completar las variables en el archivo de entorno.

## Uso con Docker

Levantar servicios:

```bash
docker compose up -d
```

Ver logs:

```bash
docker compose logs -f --tail=200
```

Detener servicios:

```bash
docker compose down
```

La API queda disponible en http://localhost:8000.

## Tests

Ejecución en contenedor (recomendado):

```bash
docker compose run --rm app python -m unittest discover -s tests
```

Ejecución reproducible estilo CI:

```bash
docker compose -f docker-compose.yml run --rm test
```

Si tenés Make instalado:

```bash
make test
make test-ci
```

## Estructura

- [docker-compose.yml](docker-compose.yml): Orquestación de servicios (API + Redis)
- [Dockerfile](Dockerfile): Imagen base para FastAPI (multi-stage con test y runtime)
- [requirements.txt](requirements.txt): Dependencias Python
- [.env.example](.env.example): Variables de entorno de ejemplo
- [app](app): Código de la aplicación
- [tests](tests): Tests automatizados

## Desarrollo local sin Docker (opcional)

1) Crear y activar un entorno virtual.
2) Instalar dependencias:

```bash
pip install -r requirements.txt
```

3) Ejecutar tests:

```bash
python -m unittest discover -s tests
```

## Monitoreo de impresoras vía CUPS

Estado de la flota vía CUPS (ready/not_ready por impresora). Para probar por interfaz:

- **Flota completa:** `GET /printers/status` — JSON con todas las impresoras y su estado.
- **Una impresora:** `GET /printers/status/{nombre}` — 404 si no existe o CUPS no disponible.

En Windows CUPS no existe y `pycups` (en `requirements.txt`) solo se instala en Linux (Raspberry Pi, WSL2 o Docker). La forma recomendada de correr la API desde Windows es usar Docker Compose o WSL2 y acceder a `http://127.0.0.1:8000`. Sin `RINE_MOCK_PRINTERS=1` verás `_cups_unavailable: true` y `printers: {}`. En Linux/Raspberry con CUPS se listan las impresoras reales.

**Testing:** Levantar la API (`python -m uvicorn app.main:app --reload`) y abrir `http://127.0.0.1:8000/docs` → probar `GET /printers/status`. O con curl: `curl http://127.0.0.1:8000/printers/status`.

#### Probar en Windows (sin CUPS)

En Windows, sin `RINE_MOCK_PRINTERS=1`, la API responde con `_cups_unavailable: true` y `printers: {}`. Para probar la misma estructura que en la Pi (impresoras de ejemplo con estado):

1. **Exportar** la variable antes de levantar la API (un `.env` no se carga automáticamente con `uvicorn`; hay que exportarla o usar el one-liner de abajo).
2. Levantar la API: `python -m uvicorn app.main:app --reload`.
3. Abrir `http://127.0.0.1:8000/docs` y probar:
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
Administrador de servicios de impresión para gestionar la cola de impresión y orquestar la comunicación con el spooler y dispositivos de impresión, recibiendo datos desde la nube y gestionando de manera centralizada por sucursal las impresiones.

