from application.use_cases.hello.get.get_hello_use_case_interface import GetHelloUseCaseInterface


class GetHelloUseCase(GetHelloUseCaseInterface):
    def __call__(self) -> dict:
        return {"message": "Rine Print Manager API is running OK!"}
