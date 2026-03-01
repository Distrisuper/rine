from application.use_cases.template.preview_label.preview_label_use_case_interface import PreviewLabelUseCaseInterface
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface
from domain.repositories.template_repository_interface import TemplateRepositoryInterface

class PreviewLabelUseCase(PreviewLabelUseCaseInterface):
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
        if not template or not template.file_path.lower().endswith(".zpl"):
            raise ValueError(f"El canal {body.channel} no está configurado con una plantilla de etiquetas (.zpl)")
        
        item = body.to_queue_item()
        return self._template_service.render(item)
