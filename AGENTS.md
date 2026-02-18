# Reglas de IA para el Proyecto RINE

Eres un experto en Python, FastAPI, y desarrollo de APIs escalables.

## Principios generales

- Preferir iteración y modularización sobre duplicación de código.
- Usar nombres descriptivos con verbos auxiliares (e.g., `is_active`, `has_permission`).
- Lowercase con underscores para archivos/directorios (e.g., `queue_service.py`).

## Python/FastAPI

- Type hints obligatorios en todas las funciones.
- Pydantic BaseModel para validación entrada/salida (nunca dicts crudos).
- Arquitectura: `router` → `controllers` → `services` → `adapters` (interfaces segregadas).
- Inyección de dependencias: pasar por parámetros, no instanciar en rutas.
- `HTTPException` solo en capa API. Services elevan `ValueError` o excepciones custom.

## Error Handling & Guard Clauses

- Validar precondiciones al inicio de funciones (guard clauses).
- Early returns para errores; happy path al final.
- Evitar else innecesarios: usar patrón if-return.
- Logging y mensajes descriptivos.

## Performance & Reliability

- Minimizar blocking I/O; usar async/await en llamadas externas.
- Lazy loading y caching en Redis para datos frecuentes.
- Pydantic serializa eficientemente.
- Middleware para logging, error monitoring, performance.

## Estilo de Código

- Seguir PEP 8. Espacios sobre tabs.
- Docstrings cortos en endpoints y servicios (1–2 líneas).
- Las entidades (modelos) deben encapsular lógica de negocio, no ser meros contenedores de datos. Aplicar **Tell, Don't Ask**.

## Arquitectura - Principios SOLID
- **Responsabilidad Única (SRP):** Una clase debería tener solo una razón para cambiar.
- Interfacear siempre: no permitas dependencias directas en lógica de negocio.
- Inyección de dependencias para testabilidad.

## Testing & Capas

- `unittest.mock` para simular servicios externos.
- Cada nueva funcionalidad incluye tests en `/tests`.
- Modelar respuestas externas con `TypedDict` o `BaseModel`.
- Rutas: `/queue/...` y parámetros en `snake_case`.
- Documentar endpoints para Swagger de manera breve y consistente.

## Comunicación
- Sé conciso. Si el cambio es pequeño, no expliques toda la teoría.
- Si ves una violación de arquitectura, corrígela antes de implementar lo nuevo.