from abc import ABC, abstractmethod
from typing import Any

class PayloadValidator(ABC):
    @abstractmethod
    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Valida y retorna el payload saneado."""
        pass
