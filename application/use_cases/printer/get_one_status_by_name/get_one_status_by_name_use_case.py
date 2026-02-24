from get_one_status_by_name_use_case_interface import GetOneStatusByNameUseCaseInterface


class GetOneStatusByNameUseCase(GetOneStatusByNameUseCaseInterface):
    def __init__(self, discovery):
        self._discovery = discovery

    def __call__(self, name: str) -> dict | None:
        return self._discovery.get_printer_status(name)
