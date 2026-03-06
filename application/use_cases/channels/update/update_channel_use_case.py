from typing import Optional
from application.use_cases.channels.update.update_channel_use_case_interface import UpdateChannelUseCaseInterface
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface

class UpdateChannelUseCase(UpdateChannelUseCaseInterface):
    def __init__(self, repo: ChannelRepositoryInterface):
        self._repo = repo

    def __call__(self, channel_id: int, description: Optional[str] = None, is_active: Optional[bool] = None, template_id: Optional[int] = None, document_source: Optional[str] = None) -> dict:
        channel = self._repo.update(channel_id, description, is_active, template_id, document_source)
        if not channel:
            raise ValueError("Channel no encontrado")
            
        return {
            "id": channel.id,
            "channel_number": channel.channel_number,
            "description": channel.description,
            "template_id": channel.template_id,
            "document_source": channel.document_source,
            "is_active": channel.is_active,
            "created_at": channel.created_at,
        }
