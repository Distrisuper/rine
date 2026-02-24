from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case_interface import GetOneStatusByNameUseCaseInterface


class GetOneStatusByNameController:
    def __init__(self, use_case: GetOneStatusByNameUseCaseInterface):
        self._use_case = use_case

    def __call__(self, name: str) -> dict | None:
        return self._use_case(name)
