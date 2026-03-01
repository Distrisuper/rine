from pydantic import BaseModel

class PrinterConfig(BaseModel):
    """Configuración de una impresora resuelta para un trabajo."""
    name: str
    is_active: bool
    printer_type: str
