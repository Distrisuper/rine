from application.use_cases.printer.get_status.get_status_use_case_interface import GetStatusUseCaseInterface


class GetStatusUseCase(GetStatusUseCaseInterface):
    def __init__(self, discovery):
        self._discovery = discovery

    def __call__(self) -> dict:
        return self._discovery.get_flota_status()
