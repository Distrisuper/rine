from sqlmodel import Session, select
from typing import Optional, List

from domain.entities.template import Template
from domain.repositories.template_repository_interface import TemplateRepositoryInterface


class TemplateRepository(TemplateRepositoryInterface):
    def __init__(self, engine):
        self.engine = engine

    def get_all(self) -> List[Template]:
        with Session(self.engine) as session:
            return list(session.exec(select(Template)).all())

    def get_by_id(self, template_id: int) -> Optional[Template]:
        with Session(self.engine) as session:
            return session.get(Template, template_id)

    def create(self, name: str, file_path: str) -> Template:
        with Session(self.engine) as session:
            template = Template(name=name, file_path=file_path)
            session.add(template)
            session.commit()
            session.refresh(template)
            return template

    def delete(self, template_id: int) -> bool:
        with Session(self.engine) as session:
            template = session.get(Template, template_id)
            if template:
                session.delete(template)
                session.commit()
                return True
            return False
