from application.use_cases.template.get_all.list_templates_use_case_interface import ListTemplatesUseCaseInterface

class ListTemplatesController:
    def __init__(self, use_case: ListTemplatesUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> list:
        return self._use_case()
