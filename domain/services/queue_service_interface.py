from abc import ABC, abstractmethod


class QueueServiceInterface(ABC):
    @abstractmethod
    async def get_next(self, limite: int, host: int) -> dict:
        pass
