from abc import ABC, abstractmethod


class CreateChannelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, channel_number: int, document_source: str, description: str | None = None, template_id: int | None = None) -> dict:
        pass
