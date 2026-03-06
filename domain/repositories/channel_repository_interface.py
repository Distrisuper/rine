from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.channel import Channel

class ChannelRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Channel]:
        pass

    @abstractmethod
    def get_by_id(self, channel_id: int) -> Optional[Channel]:
        pass

    @abstractmethod
    def get_by_number(self, channel_number: int) -> Optional[Channel]:
        pass

    @abstractmethod
    def create(self, channel_number: int, document_source: str, description: str = None, template_id: int = None) -> Channel:
        pass

    @abstractmethod
    def update(self, channel_id: int, description: str = None, is_active: bool = None, template_id: int = None, document_source: str = None) -> Optional[Channel]:
        pass

    @abstractmethod
    def delete(self, channel_id: int) -> bool:
        pass

