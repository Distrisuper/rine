from application.use_cases.health.health_use_case_interface import HealthUseCaseInterface


class HealthController:
    def __init__(self, use_case: HealthUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> dict:
        return self._use_case()
