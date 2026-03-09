import json
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union, Any, Dict


class RemitoPreviewRequestDTO(BaseModel):
    channel: int = 0
    location: str = ""
    extra_data: Optional[str] = None
    client_code: str = ""
    client_name: str = "Cliente prueba"
    order_number: int = 1
    invoice_total: Optional[float] = None
    redi_id: int = 0
    server: Optional[str] = None
    ds: Optional[str] = None
    
    # Parámetros para Query String (Remito)
    address: Optional[str] = None
    city: Optional[str] = None
    items: Optional[str] = None  # JSON array as string
    total: Optional[float] = None
    remito_id: Optional[str] = None
    fecha: Optional[str] = None
    reparto: Optional[str] = None
    sucursal: Optional[str] = None
    obs: Optional[str] = None
    comentarios: Optional[str] = None
    cant_unidades: Optional[str] = None
    valor_declarado: Optional[str] = None
    numero_cot: Optional[str] = None
    numero_cai: Optional[str] = None
    vencimiento: Optional[str] = None
    disclaimer: Optional[str] = None

    @model_validator(mode='after')
    def pack_extra_data(self) -> 'RemitoPreviewRequestDTO':
        # Si extra_data está vacío pero tenemos los campos individuales, los empaquetamos como JSON
        if not self.extra_data:
            try:
                items_list = json.loads(self.items) if self.items else []
            except:
                items_list = []

            data = {
                "remito_id": self.remito_id or "",
                "fecha": self.fecha or "",
                "reparto": self.reparto or "",
                "sucursal": self.sucursal or "",
                "address": self.address or "",
                "city": self.city or "",
                "items": items_list,
                "total": self.total or 0.0,
                "obs": self.obs or "",
                "comentarios": self.comentarios or "",
                "cant_unidades": self.cant_unidades or "",
                "valor_declarado": self.valor_declarado or "",
                "numero_cot": self.numero_cot or "",
                "numero_cai": self.numero_cai or "",
                "vencimiento": self.vencimiento or "",
                "disclaimer": self.disclaimer or ""
            }
            self.extra_data = json.dumps(data)
            
            # Sincronizamos invoice_total con total si es necesario
            if self.total and not self.invoice_total:
                self.invoice_total = self.total
                
        return self


class RemitoItem(BaseModel):
    codigo: str = ""
    cantidad: Union[int, float, str] = 0
    descripcion: str = ""


class RemitoPreviewPostRequestDTO(BaseModel):
    """Body JSON para preview de remito — sin encodear items."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "client_code": "CLI001",
                "client_name": "Super Distribuidora SA",
                "order_number": 9999,
                "remito_id": "R-2026-00042",
                "fecha": "09/03/2026",
                "address": "Av. Corrientes 1234",
                "city": "Buenos Aires",
                "reparto": "Reparto Norte",
                "sucursal": "MDP",
                "obs": "Sin observaciones",
                "cant_unidades": "18",
                "valor_declarado": "45000",
                "numero_cot": "COT-88776",
                "numero_cai": "CAI-1234567",
                "vencimiento": "31/12/2026",
                "total": 45000.0,
                "items": [
                    {"codigo": "VTH5480", "cantidad": 2, "descripcion": "BUJE BARRA DIRECCION VW GOL GACEL SENDA"},
                    {"codigo": "VTH5798", "cantidad": 2, "descripcion": "BUJE PARRILLA RENAULT KANGOO CLIO II SYMBOL"},
                    {"codigo": "VTH8473", "cantidad": 2, "descripcion": "BUJE PARRILLA VW AMAROK INFERIOR PARTE DELANTERA"},
                    {"codigo": "VTH8475", "cantidad": 2, "descripcion": "BUJE ESTABILIZADORA VW AMAROK DELANTERA"},
                    {"codigo": "VTH8436", "cantidad": 2, "descripcion": "BUJE PARRILLA VW GOLF BORA GOL TREND PASSAT"},
                    {"codigo": "VTH7777", "cantidad": 2, "descripcion": "BUJE ESTABILIZADORA RENAULT DUSTER"},
                ],
            }
        }
    }

    channel: int = 0
    client_code: str = ""
    client_name: str = "Cliente prueba"
    order_number: int = 1
    remito_id: Optional[str] = None
    fecha: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    items: List[RemitoItem] = Field(default_factory=list)
    total: Optional[float] = None
    reparto: Optional[str] = None
    sucursal: Optional[str] = None
    obs: Optional[str] = None
    comentarios: Optional[str] = None
    cant_unidades: Optional[str] = None
    valor_declarado: Optional[str] = None
    numero_cot: Optional[str] = None
    numero_cai: Optional[str] = None
    vencimiento: Optional[str] = None
    disclaimer: Optional[str] = None

    def to_get_dto(self) -> RemitoPreviewRequestDTO:
        """Convierte a RemitoPreviewRequestDTO con extra_data empaquetado."""
        items_dicts = [item.model_dump() for item in self.items]
        data = {
            "remito_id": self.remito_id or "",
            "fecha": self.fecha or "",
            "reparto": self.reparto or "",
            "sucursal": self.sucursal or "",
            "address": self.address or "",
            "city": self.city or "",
            "items": items_dicts,
            "total": self.total or 0.0,
                "obs": self.obs or "",
                "comentarios": self.comentarios or "",
                "cant_unidades": self.cant_unidades or "",
                "valor_declarado": self.valor_declarado or "",
                "numero_cot": self.numero_cot or "",
                "numero_cai": self.numero_cai or "",
                "vencimiento": self.vencimiento or "",
                "disclaimer": self.disclaimer or "",
        }
        return RemitoPreviewRequestDTO(
            channel=self.channel,
            client_code=self.client_code,
            client_name=self.client_name,
            order_number=self.order_number,
            invoice_total=self.total,
            extra_data=json.dumps(data),
        )
