from application.use_cases.example.get.get_example_use_case_interface import (
    GetExampleUseCaseInterface,
)


class GetExampleUseCase(GetExampleUseCaseInterface):
    def __call__(self) -> dict:
        return {"message": "Example Flow: Welcome to Rine Print Manager API"}
