from abc import ABC, abstractmethod
from typing import Any


class DiscoverPrinterUseCaseInterface(ABC):
    @abstractmethod
    def __call__(self) -> list[dict[str, Any]]:
        """Retorna lista de impresoras descobertas."""
        pass
