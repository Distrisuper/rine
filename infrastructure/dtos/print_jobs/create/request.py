from pydantic import BaseModel, Field
from typing import Dict, Any


class CreatePrintJobRequestDTO(BaseModel):
    channel: str = Field(..., description="Numero de canal como string numerico. Ej: '4'")
    client_code: str = Field(..., description="Codigo del cliente")
    client_name: str = Field(..., description="Nombre del cliente")
    payload: Dict[str, Any] = Field(..., description="Objeto JSON con los datos del documento")
    number_of_copies: str | None = Field(
        default="1",
        description="Cantidad de copias como string numerico entre 1 y 100. Ej: '1'",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "channel": "4",
                    "client_code": "05451",
                    "client_name": "REPUESJOR SRL",
                    "payload": {
                        "client_code": "05451",
                        "client_name": "REPUESJOR SRL",
                        "order_number": "PED-2026-00045",
                        "address": "Av. Colon 1234",
                        "city": "Mar del Plata",
                        "items": [
                            {"descripcion": "Filtro de aceite", "cantidad": "2"},
                            {"descripcion": "Correa distribucion", "cantidad": "1"},
                        ],
                        "total": "185000.50",
                        "remito_id": "REM-000987",
                        "fecha": "2026-03-17",
                    },
                    "number_of_copies": "1",
                }
            ]
        }
    }
