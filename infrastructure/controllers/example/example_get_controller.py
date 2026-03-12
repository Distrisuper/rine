from application.use_cases.example.get.get_example_use_case_interface import (
    GetExampleUseCaseInterface,
)


class ExampleGetController:
    def __init__(self, use_case: GetExampleUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> dict:
        return self._use_case()
