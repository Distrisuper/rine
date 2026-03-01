from application.use_cases.channels.create.create_channel_use_case_interface import (
    CreateChannelUseCaseInterface,
)
from domain.entities.channel import Channel
from domain.repositories.channel_repository import ChannelRepository
from infrastructure.db.database import engine
from sqlmodel import Session


class CreateChannelUseCase(CreateChannelUseCaseInterface):
    def __call__(self, channel_number: int, description: str | None, template_id: int) -> dict:
        repo = ChannelRepository(engine)

        existing = repo.get_by_number(channel_number)
        if existing:
            raise ValueError(f"Channel {channel_number} ya existe")

        channel = Channel(
            channel_number=channel_number,
            description=description,
            template_id=template_id,
        )

        with Session(engine) as session:
            session.add(channel)
            session.commit()
            session.refresh(channel)

        return {
            "id": channel.id,
            "channel_number": channel.channel_number,
            "description": channel.description,
            "template_id": channel.template_id,
            "is_active": channel.is_active,
            "created_at": channel.created_at,
        }
