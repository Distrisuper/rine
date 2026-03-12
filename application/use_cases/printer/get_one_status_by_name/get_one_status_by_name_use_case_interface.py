from abc import ABC, abstractmethod


class GetOneStatusByNameUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, name: str) -> dict | None:
        pass
