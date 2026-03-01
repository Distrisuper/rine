from abc import ABC, abstractmethod


class HealthUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> dict:
        pass
