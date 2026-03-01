from typing import List
from application.use_cases.template.get_all.list_templates_use_case_interface import ListTemplatesUseCaseInterface
from domain.repositories.template_repository_interface import TemplateRepositoryInterface

class ListTemplatesUseCase(ListTemplatesUseCaseInterface):
    def __init__(self, repo: TemplateRepositoryInterface):
        self._repo = repo

    def __call__(self) -> List[dict]:
        templates = self._repo.get_all()
        return [
            {
                "id": t.id,
                "name": t.name,
                "file_path": t.file_path,
                "created_at": t.created_at,
            }
            for t in templates
        ]
