from application.use_cases.printer.get_all.list_printers_use_case_interface import ListPrintersUseCaseInterface

class ListPrintersController:
    def __init__(self, use_case: ListPrintersUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> list:
        return self._use_case()
