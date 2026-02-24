from abc import ABC, abstractmethod


class GetHelloUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> dict:
        pass
