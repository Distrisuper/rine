from abc import ABC, abstractmethod
from typing import Optional


class CreateChannelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, channel_number: int, description: str | None, template_id: Optional[int]) -> dict:
        pass
