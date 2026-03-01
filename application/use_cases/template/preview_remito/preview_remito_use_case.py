from application.use_cases.template.preview_remito.preview_remito_use_case_interface import PreviewRemitoUseCaseInterface
from domain.repositories.channel_repository import ChannelRepository
from domain.repositories.template_repository import TemplateRepository

class PreviewRemitoUseCase(PreviewRemitoUseCaseInterface):
    def __init__(
        self,
        template_service,
        channel_repo: ChannelRepository,
        template_repo: TemplateRepository
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
        
        item = body.to_queue_item()
        return self._template_service.render(item)
