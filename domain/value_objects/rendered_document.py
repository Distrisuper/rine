from pydantic import BaseModel

class RenderedDocument(BaseModel):
    """Paquete de datos de un documento renderizado listo para imprimir o previsualizar."""
    content: bytes
    content_type: str  # "pdf" o "zpl"
    title: str         # "Etiqueta", "Remito", etc.
