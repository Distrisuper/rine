from abc import ABC, abstractmethod
from typing import Any
from sqlmodel import Session
from domain.value_objects.rendered_document import RenderedDocument


class DocumentBuilder(ABC):
    @abstractmethod
    def build(self, job: Any, session: Session) -> RenderedDocument:
        pass
