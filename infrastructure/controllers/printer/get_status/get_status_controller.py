from application.use_cases.printer.get_status.get_status_use_case_interface import GetStatusUseCaseInterface


class GetStatusController:
    def __init__(self, use_case: GetStatusUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> dict:
        return self._use_case()
