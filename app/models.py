from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional, Literal


class PrintJobStatus(StrEnum):
    """Estados de un trabajo de impresión."""

    PENDIENTE = "PENDIENTE"
    IMPRIMIENDO = "IMPRIMIENDO"
    ERROR = "ERROR"
    FINALIZADO = "FINALIZADO"

class QueueItem(BaseModel):
    """Ítem en la cola de impresión."""

    id: int
    client_id: str
    client_code: str
    client_name: str
    order_number: int
    type: str
    type_code: int | str | None = None
    channel: int
    invoice_type: Optional[str] = None
    invoice_number: int | str | None = None
    invoice_comment: str
    invoice_total: Optional[float] = None
    result: int
    result_detail: str
    retry: int
    priority: int
    printed: int
    print_count: int
    host: int
    redi_code: str
    redi_id: int
    date_created: str
    date_started: Optional[str] = None
    date_processed: Optional[str] = None
    extra_data: Optional[str] = None


class PrintQueueResponse(BaseModel):
    """Respuesta del endpoint de cola de impresión."""

    ok: int
    data: list[QueueItem]

class PrintRequest(BaseModel):
    """
    Solicitud unificada para impresión.

    ## Tipos de impresión y campos requeridos:

    ### ETIQ (Etiqueta)
    - **Obligatorios**: type, client_code, client_name, redi_code, id_remito

    ### REMI (Remito)
    - **Obligatorios**: type, client_code, client_name, redi_code, id_remito

    ### GM (Pedido de impresión)
    - **Obligatorios**: type, client_code, client_name, redi_code, id_remito

    ### PEND (Redi pendiente)
    - **Obligatorios**: type, client_code, client_name, redi_code, id_remito
    """

    type: Literal["ETIQ", "REMI", "GM", "PEND"] = Field(
        ...,
        description="Tipo de comprobante a imprimir",
        examples=["ETIQ"]
    )
    client_code: str = Field(..., description="Código del cliente", examples=["06689"])
    client_name: str = Field(..., description="Nombre del cliente", examples=["Sergio Palomo"])
    set_host: Optional[int] = Field(None, description="Identificador del host (opcional)", examples=[301])
    redi_code: str = Field(..., description="Código REDI", examples=["[R5-12345]__"])
    id_remito: str = Field(..., description="ID del remito", examples=["685110"])

    # Campos opcionales según tipo
    client_address: Optional[str] = Field(
        None,
        description="Dirección del cliente (requerido para ETIQ, REMI)",
        examples=["Calle Principal 123"]
    )
    client_city: Optional[str] = Field(
        None,
        description="Ciudad del cliente (requerido para ETIQ, REMI)",
        examples=["Buenos Aires"]
    )
    location: Optional[str] = Field(
        None,
        description="Ubicación/sucursal (opcional)",
        examples=["BA"]
    )
    transport_description: Optional[str] = Field(
        None,
        description="Descripción del transporte (opcional)",
        examples=["El Rapido S.A."]
    )
    package_quantity: Optional[int] = Field(
        None,
        description="Cantidad de paquetes (requerido para ETIQ, PEND)",
        examples=[5],
        ge=1
    )
    label_packages: Optional[int] = Field(
        None,
        description="Cantidad de etiquetas (requerido para ETIQ, REMI)",
        examples=[1],
        ge=1
    )
    remitos_quantity: Optional[int] = Field(
        None,
        description="Cantidad de remitos (requerido para REMI)",
        examples=[3],
        ge=1
    )
    invoices_quantity: Optional[int] = Field(
        None,
        description="Cantidad de comprobantes (requerido para GM)",
        examples=[1],
        ge=1
    )
    pending: Optional[bool] = Field(
        None,
        description="Indica si el remito es pendiente (True) o no (False) (requerido para PEND)",
        examples=[True],
    )


class PrintResponse(BaseModel):
    """Respuesta genérica de impresión."""

    ok: int
    message: str
    doc_type: str


class PrintJobRecord(BaseModel):
    """Registro persistido de un trabajo de impresión."""

    id: int
    status: PrintJobStatus
    date_created: str
    date_processed: Optional[str] = None