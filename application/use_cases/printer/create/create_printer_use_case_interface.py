from abc import ABC, abstractmethod
from typing import List

class CreatePrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, name: str, channel_ids: List[int]) -> dict:
        pass
