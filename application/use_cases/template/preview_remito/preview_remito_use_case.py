from application.use_cases.template.preview_remito.preview_remito_use_case_interface import PreviewRemitoUseCaseInterface
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface
from domain.repositories.template_repository_interface import TemplateRepositoryInterface
from domain.value_objects.queue_item import QueueItem

class PreviewRemitoUseCase(PreviewRemitoUseCaseInterface):
    def __init__(
        self,
        template_service,
        channel_repo: ChannelRepositoryInterface,
        template_repo: TemplateRepositoryInterface
    ):
        self._template_service = template_service
        self._channel_repo = channel_repo
        self._template_repo = template_repo

    def __call__(self, body) -> bytes:
        # Validar canal dinámicamente desde la DB
        channel = self._channel_repo.get_by_number(body.channel)
        if not channel:
            raise ValueError(f"El canal {body.channel} no existe")
            
        if not channel.template_id:
            raise ValueError(f"El canal {body.channel} no tiene una plantilla asociada")
            
        template = self._template_repo.get_by_id(channel.template_id)
        if not template or not template.file_path.lower().endswith(".html"):
            raise ValueError(f"El canal {body.channel} no está configurado con una plantilla de remitos (.html)")
        
        # Mapeo manual de DTO a QueueItem
        item = QueueItem(
            id=0,
            client_id="",
            client_code=body.client_code,
            client_name=body.client_name,
            order_number=body.order_number,
            type="PREVIEW",
            type_code=0,
            location=body.location,
            channel=body.channel,
            invoice_type="",
            invoice_number=0,
            invoice_comment="",
            invoice_total=body.invoice_total,
            result=0,
            result_detail="",
            retry=0,
            priority=0,
            printed=0,
            print_count=0,
            host=0,
            redi_code="",
            redi_id=body.redi_id,
            date_created="",
            extra_data=body.extra_data,
            server=body.server,
            ds=body.ds
        )
        
        return self._template_service.render(item)
