from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.template import Template

class TemplateRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Template]:
        pass

    @abstractmethod
    def get_by_id(self, template_id: int) -> Optional[Template]:
        pass

    @abstractmethod
    def create(self, name: str, file_path: str) -> Template:
        pass

    @abstractmethod
    def delete(self, template_id: int) -> bool:
        pass
