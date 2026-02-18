# RINE Print Manager

Repositorio base para el administrador de impresión dockerizado en Raspberry Pi.

## Objetivo

Administrador de servicios de impresión para gestionar la cola de impresión y orquestar la comunicación con el spooler y dispositivos de impresión, recibiendo datos desde la nube y gestionando de manera centralizada por sucursal las impresiones.

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
