from typing import Literal
from pydantic import BaseModel

class ResolvedTemplate(BaseModel):
    """Resultado del resolver: template a usar y tipo de salida."""
    template_id: str
    output_type: Literal["pdf", "zpl"]
