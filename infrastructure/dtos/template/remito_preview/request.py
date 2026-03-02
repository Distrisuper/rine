import json
from pydantic import BaseModel, model_validator
from typing import Optional, List, Any


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
