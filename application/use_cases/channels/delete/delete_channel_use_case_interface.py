from abc import ABC, abstractmethod

class DeleteChannelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, channel_id: int) -> bool:
        pass
