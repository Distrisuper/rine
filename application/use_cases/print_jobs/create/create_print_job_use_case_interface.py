from abc import ABC, abstractmethod
from datetime import datetime


class CreatePrintJobUseCaseInterface(ABC):
    @abstractmethod
    def __call__(
        self,
        channel: int,
        client_code: str,
        client_name: str,
        payload: dict,
        number_of_copies: int,
    ) -> dict:
        pass
