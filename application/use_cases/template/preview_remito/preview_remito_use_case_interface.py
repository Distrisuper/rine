from abc import ABC, abstractmethod

class PreviewRemitoUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, data) -> dict:
        pass
