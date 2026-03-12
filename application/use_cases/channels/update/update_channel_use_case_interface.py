from abc import ABC, abstractmethod
from typing import Optional

class UpdateChannelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, channel_id: int, description: Optional[str], is_active: Optional[bool], template_id: Optional[int], document_source: Optional[str]) -> dict:
        pass
