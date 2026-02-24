from get_next_use_case_interface import GetNextUseCaseInterface


class GetNextUseCase(GetNextUseCaseInterface):
    def __init__(self, queue_service):
        self._queue_service = queue_service

    async def __call__(self, limit: int, host: int) -> dict:
        return await self._queue_service.get_next(limit, host)
