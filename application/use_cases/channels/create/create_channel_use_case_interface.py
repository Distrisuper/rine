from abc import ABC, abstractmethod


class CreateChannelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, channel_number: int, description: str | None, template_id: int) -> dict:
        pass
