from abc import ABC, abstractmethod

class DeletePrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self, printer_id: int) -> bool:
        pass
