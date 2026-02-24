from application.use_cases.hello.get.get_hello_use_case_interface import GetHelloUseCaseInterface


class HelloGetController:
    def __init__(self, use_case: GetHelloUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> dict:
        return self._use_case()
