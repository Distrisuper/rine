from abc import ABC, abstractmethod

class PreviewRemitoUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, body) -> bytes:
        pass
