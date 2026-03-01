from typing import Optional
from application.use_cases.channels.update.update_channel_use_case_interface import UpdateChannelUseCaseInterface
from domain.repositories.channel_repository import ChannelRepository

class UpdateChannelUseCase(UpdateChannelUseCaseInterface):
    def __init__(self, repo: ChannelRepository):
        self._repo = repo

    def __call__(self, channel_id: int, description: Optional[str], is_active: Optional[bool], template_id: Optional[int]) -> dict:
        channel = self._repo.update(channel_id, description, is_active, template_id)
        if not channel:
            return None
            
        return {
            "id": channel.id,
            "channel_number": channel.channel_number,
            "description": channel.description,
            "template_id": channel.template_id,
            "is_active": channel.is_active,
            "created_at": channel.created_at,
        }
