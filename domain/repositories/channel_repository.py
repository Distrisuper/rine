from sqlmodel import Session, select
from typing import Optional

from domain.entities.channel import Channel


class ChannelRepository:
    def __init__(self, engine):
        self.engine = engine

    def get_all(self) -> list[Channel]:
        with Session(self.engine) as session:
            return list(session.exec(select(Channel).order_by(Channel.channel_number)).all())

    def get_by_id(self, channel_id: int) -> Optional[Channel]:
        with Session(self.engine) as session:
            return session.get(Channel, channel_id)

    def get_by_number(self, channel_number: int) -> Optional[Channel]:
        with Session(self.engine) as session:
            statement = select(Channel).where(Channel.channel_number == channel_number)
            return session.exec(statement).first()

    def create(self, channel_number: int, description: str = None, template_id: int = None) -> Channel:
        with Session(self.engine) as session:
            channel = Channel(channel_number=channel_number, description=description, template_id=template_id)
            session.add(channel)
            session.commit()
            session.refresh(channel)
            return channel

    def update(self, channel_id: int, description: str = None, is_active: bool = None, template_id: int = None) -> Optional[Channel]:
        with Session(self.engine) as session:
            channel = session.get(Channel, channel_id)
            if not channel:
                return None
            
            if description is not None:
                channel.description = description
            if is_active is not None:
                channel.is_active = is_active
            if template_id is not None:
                channel.template_id = template_id
            
            session.commit()
            session.refresh(channel)
            return channel

    def delete(self, channel_id: int) -> bool:
        with Session(self.engine) as session:
            channel = session.get(Channel, channel_id)
            if channel:
                session.delete(channel)
                session.commit()
                return True
            return False
