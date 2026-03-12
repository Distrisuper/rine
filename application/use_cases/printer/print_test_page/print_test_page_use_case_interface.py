from abc import ABC, abstractmethod

class PrintTestPageUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, printer_id: int) -> dict:
        pass
