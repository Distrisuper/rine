from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase


class CreatePrintJobController:
    def __init__(self, use_case: CreatePrintJobUseCase):
        self._use_case = use_case

    def __call__(self, channel: int, client_code: str, client_name: str, payload: dict, number_of_copies: int) -> dict:
        return self._use_case(channel, client_code, client_name, payload, number_of_copies)
