from typing import List
from application.use_cases.channels.get_all.list_channels_use_case_interface import ListChannelsUseCaseInterface
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface
from domain.repositories.template_repository_interface import TemplateRepositoryInterface

class ListChannelsUseCase(ListChannelsUseCaseInterface):
    def __init__(self, channel_repo: ChannelRepositoryInterface, template_repo: TemplateRepositoryInterface):
        self._channel_repo = channel_repo
        self._template_repo = template_repo

    def __call__(self) -> List[dict]:
        channels = self._channel_repo.get_all()
        templates = {t.id: t.name for t in self._template_repo.get_all()}
        
        return [
            {
                "id": c.id,
                "channel_number": c.channel_number,
                "description": c.description,
                "template_id": c.template_id,
                "template_name": templates.get(c.template_id),
                "is_active": c.is_active,
                "created_at": c.created_at,
            }
            for c in channels
        ]
