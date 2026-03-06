from abc import ABC, abstractmethod
from typing import Any
from sqlmodel import Session


class DocumentBuilder(ABC):
    @abstractmethod
    def build(self, job: Any, session: Session) -> bytes:
        pass
