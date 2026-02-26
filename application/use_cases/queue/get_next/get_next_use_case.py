from application.use_cases.queue.get_next.get_next_use_case_interface import GetNextUseCaseInterface
from domain.services.queue_service_interface import QueueServiceInterface


class GetNextUseCase(GetNextUseCaseInterface):
    def __init__(self, queue_service: QueueServiceInterface):
        self._queue_service = queue_service

    async def __call__(self, limit: int, host: int) -> dict:
        return await self._queue_service.get_next(limit, host)
