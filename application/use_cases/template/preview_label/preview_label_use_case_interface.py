from abc import ABC, abstractmethod


class PreviewLabelUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, body) -> bytes:
        pass
