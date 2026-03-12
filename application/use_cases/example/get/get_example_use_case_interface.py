from abc import ABC, abstractmethod


class GetExampleUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> dict:
        pass
