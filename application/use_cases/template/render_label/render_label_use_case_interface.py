from abc import ABC, abstractmethod


class RenderLabelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, body) -> bytes:
        pass
