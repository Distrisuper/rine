# Guía de Implementación: Flujo de una Petición (API Flow)

Este documento detalla el patrón arquitectónico para exponer nuevos endpoints en la API. El objetivo es mantener el **Dominio** puro y desacoplado de la **Infraestructura**.

---

## 🟢 El Camino de una Petición (Step-by-Step)

Para implementar un endpoint, los datos deben viajar a través de estas capas en este orden:

### 1. Definición del Contrato (DTOs)
*   **Ubicación:** `infrastructure/dtos/[modulo]/[accion]/`
*   **Propósito:** Validar la entrada y formatear la salida.
*   **Herramienta:** Pydantic `BaseModel`.
*   **Ejemplo:** `CreatePrinterRequestDTO` (entrada) y `PrinterResponseDTO` (salida).

### 2. La Ruta (Routing)
*   **Ubicación:** `infrastructure/api/routes.py`
*   **Propósito:** Definir el método HTTP, la URL y delegar la ejecución al Controlador.
*   **Responsabilidad:** Inyectar el controlador mediante `Depends(container.xxx)`.

### 3. El Controlador (Controller)
*   **Ubicación:** `infrastructure/controllers/[modulo]/[accion]/`
*   **Propósito:** Es un puente delgado ("thin bridge"). 
*   **Responsabilidad:** Recibir el DTO de la ruta, llamar al Caso de Uso y convertir el resultado en una respuesta HTTP (o retornar el DTO de salida).

### 4. La Interfaz del Caso de Uso (Contract)
*   **Ubicación:** `application/use_cases/[modulo]/[accion]/[nombre]_interface.py`
*   **Propósito:** Definir qué hace el negocio sin decir cómo. Es vital para el desacoplamiento y el testing.

### 5. El Caso de Uso (Orchestrator)
*   **Ubicación:** `application/use_cases/[modulo]/[accion]/[nombre]_use_case.py`
*   **Propósito:** Ejecutar la lógica de negocio.
*   **Responsabilidad:** Coordinar Repositorios y Servicios de Dominio. No sabe nada de HTTP ni de bases de datos específicas.

### 6. El Repositorio (Persistence)
*   **Ubicación:** `infrastructure/repositories/` (Implementación) y `domain/repositories/` (Interfaz).
*   **Propósito:** Consultar o persistir datos.
*   **Herramienta:** SQLAlchemy / SQLModel.

---

## 🛠 Ejemplo Práctico: Crear una Impresora

### Paso 1: DTO de Entrada (`infrastructure/dtos/printers/create/request.py`)
```python
from pydantic import BaseModel

class CreatePrinterRequest(BaseModel):
    name: str
    channel_ids: list[int] = []
```

### Paso 2: Interfaz del Caso de Uso (`application/use_cases/printer/create/interface.py`)
```python
from abc import ABC, abstractmethod

class CreatePrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, name: str, channel_ids: list[int]):
        pass
```

### Paso 3: Caso de Uso (`application/use_cases/printer/create/create_printer_use_case.py`)
```python
class CreatePrinterUseCase(CreatePrinterUseCaseInterface):
    def __init__(self, printer_repo: PrinterRepositoryInterface):
        self._repo = printer_repo

    def __call__(self, name: str, channel_ids: list[int]):
        # Lógica de negocio (ej: validar nombre duplicado)
        return self._repo.create_printer(name, channel_ids)
```

### Paso 4: Controlador (`infrastructure/controllers/printer/create/create_printer_controller.py`)
```python
class CreatePrinterController:
    def __init__(self, use_case: CreatePrinterUseCaseInterface):
        self._use_case = use_case

    def __call__(self, name: str, channel_ids: list[int]):
        return self._use_case(name, channel_ids)
```

### Paso 5: Ruta (`infrastructure/api/routes.py`)
```python
@router.post("/printers", response_model=PrinterResponse)
def create_printer(
    request: CreatePrinterRequest,
    controller: CreatePrinterController = Depends(container.create_printer_controller)
):
    return controller(request.name, request.channel_ids)
```

---

## 🔗 Inyección de Dependencias (`infrastructure/api/container.py`)

Todo debe estar "cableado" en el `Container`. Es el único lugar donde la infraestructura se instancia y se pasa al dominio.

```python
# Dentro de la clase Container
@lru_cache
def init_create_printer_controller(self) -> CreatePrinterController:
    # Se inyecta la implementación del repo (infra) en el caso de uso (app)
    use_case = CreatePrinterUseCase(self._printer_repo) 
    return CreatePrinterController(use_case)
```

---

## ✅ Checklist para nuevos Endpoints

1. [ ] ¿Creaste los **DTOs** de entrada/salida?
2. [ ] ¿Definiste la **Interfaz** del Caso de Uso?
3. [ ] ¿Implementaste el **Caso de Uso** usando solo interfaces de repositorios?
4. [ ] ¿Implementaste el método necesario en el **Repositorio**?
5. [ ] ¿Creaste el **Controlador**?
6. [ ] ¿Registraste todo en el **Container**?
7. [ ] ¿Agregaste la **Ruta** en `routes.py`?
8. [ ] ¿Escribiste un test **E2E** en `tests/e2e/`?

---

**Nota para Agentes:** Si se te pide crear un endpoint, sigue este orden estrictamente. No omitas la interfaz del caso de uso ni el registro en el contenedor.

---

### 📖 Referencias y Estándares

#### ¿Qué estándar es este?
Este proyecto sigue una arquitectura **Hexagonal** (también conocida como *Ports and Adapters*) combinada con principios de **DDD** (*Domain-Driven Design*). 

En este esquema:
*   **El Dominio es el núcleo:** Las reglas de negocio no dependen de si usamos FastAPI, SQLModel o una impresora Zebra.
*   **La Infraestructura es un detalle:** La base de datos, la API y los drivers de impresión son piezas intercambiables que "se enchufan" al núcleo.

#### ¿Qué ganamos trabajando así?
1.  **Mantenibilidad (Futuro):** Si mañana decidimos cambiar SQLite por PostgreSQL o FastAPI por otro framework, el 80% del código (Use Cases y Entidades) permanece intacto.
2.  **Testabilidad Total:** Al usar interfaces (`ABC`), podemos testear la lógica de negocio simulando la base de datos o las impresoras de forma ultra rápida y sin efectos secundarios.
3.  **Desacoplamiento:** Un error en la validación de la API (Infra) no puede romper la lógica de cálculo de un remito (Dominio).
4.  **Paralelismo:** Un desarrollador puede trabajar en el diseño del PDF mientras otro trabaja en la lógica de persistencia, ya que ambos están unidos por un contrato (Interfaz) predefinido.

#### Enlaces recomendados para profundizar:
*   [Arquitectura Hexagonal (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
*   [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
*   [Clean Architecture en Python (Guía práctica)](https://www.cosmicpython.com/book/preface.html)
