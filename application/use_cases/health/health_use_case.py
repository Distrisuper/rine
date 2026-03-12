from application.use_cases.health.health_use_case_interface import HealthUseCaseInterface


class HealthUseCase(HealthUseCaseInterface):
    def __call__(self) -> dict:
        return {"status": "ok"}
