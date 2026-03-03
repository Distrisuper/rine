from application.use_cases.channels.create.create_channel_use_case_interface import (
    CreateChannelUseCaseInterface,
)
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface
from typing import Optional


class CreateChannelUseCase(CreateChannelUseCaseInterface):
    def __init__(self, repo: ChannelRepositoryInterface):
        self._repo = repo

    def __call__(self, channel_number: int, description: str | None, template_id: Optional[int]) -> dict:
        existing = self._repo.get_by_number(channel_number)
        if existing:
            raise ValueError(f"Channel {channel_number} ya existe")

        channel = self._repo.create(
            channel_number=channel_number,
            description=description,
            template_id=template_id,
        )

        return {
            "id": channel.id,
            "channel_number": channel.channel_number,
            "description": channel.description,
            "template_id": channel.template_id,
            "is_active": channel.is_active,
            "created_at": channel.created_at,
        }
