from abc import ABC, abstractmethod


class GetStatusUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> dict:
        pass
