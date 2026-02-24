from abc import ABC, abstractmethod


class RenderRemitoUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, body) -> bytes:
        pass
