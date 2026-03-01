from abc import ABC, abstractmethod

class TestPrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, printer_id: int) -> dict:
        pass
