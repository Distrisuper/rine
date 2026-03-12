from abc import ABC, abstractmethod
from typing import List

class ListTemplatesUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> List[dict]:
        pass
