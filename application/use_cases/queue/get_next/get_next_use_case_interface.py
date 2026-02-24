from abc import ABC, abstractmethod


class GetNextUseCaseInterface(ABC):
    @abstractmethod
    async def __call__(self, limit: int, host: int) -> dict:
        pass
