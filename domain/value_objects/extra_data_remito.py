from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError

class ExtraDataRemito(BaseModel):
    """
    Datos extra del ítem de cola (remito/etiqueta).
    Parsea el JSON de extra_data.
    Campos legacy (etiquetas) y campos de remito HTML coexisten como opcionales.
    """
    # --- campos legacy (etiquetas / S3) ---
    remito: Optional[str] = None
    ftp_filename: Optional[str] = None
    label_to: Optional[str] = None
    label_address: Optional[str] = None
    label_city: Optional[str] = None
    label_packages: Optional[str] = None
    label_transport: Optional[str] = None
    idRemito: Optional[str] = None
    redi_id: Optional[str] = None

    # --- campos de remito HTML ---
    remito_id: Optional[str] = None
    fecha: Optional[str] = None
    reparto: Optional[str] = None
    sucursal: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    total: Optional[float] = None
    obs: Optional[str] = None
    comentarios: Optional[str] = None
    cant_unidades: Optional[str] = None
    valor_declarado: Optional[str] = None
    numero_cot: Optional[str] = None
    numero_cai: Optional[str] = None
    vencimiento: Optional[str] = None
    disclaimer: Optional[str] = None

    @classmethod
    def from_json(cls, raw: str | None) -> ExtraDataRemito | None:
        """Parsea el JSON de extra_data; devuelve None si está vacío o es inválido."""
        if not raw or not raw.strip():
            return None
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                return None
            return cls.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            return None
