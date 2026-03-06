import pytest
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from pydantic import BaseModel, field_validator, ValidationError
from infrastructure.api.exceptions import validation_exception_handler

class TestDTO(BaseModel):
    source: str

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v == "INVALID":
            raise ValueError("Mensaje de error personalizado")
        return v

@pytest.mark.asyncio
async def test_validation_exception_handler_serialization_error():
    # Simulamos el fallo de validación de Pydantic
    try:
        TestDTO(source="INVALID")
    except ValidationError as e:
        # Envolvemos en RequestValidationError como hace FastAPI
        request_exc = RequestValidationError(e.errors())
        
        # El handler debería devolver un JSONResponse
        # Si falla la serialización, JSONResponse lanzará TypeError internamente cuando se intente leer el body
        response = await validation_exception_handler(None, request_exc)
        
        # Accedemos al body para forzar la serialización si es perezosa (lazy)
        try:
            body = response.body
            assert b"detail" in body
            assert b"Mensaje de error personalizado" in body
            print("Serialización exitosa")
        except TypeError as e:
            pytest.fail(f"Fallo de serialización JSON: {e}")
