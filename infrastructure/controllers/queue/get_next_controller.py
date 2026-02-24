from application.use_cases.queue.get_next.get_next_use_case_interface import GetNextUseCaseInterface


class GetNextController:
    def __init__(self, use_case: GetNextUseCaseInterface):
        self._use_case = use_case

    async def __call__(self, limit: int, host: int) -> dict:
        return await self._use_case(limit, host)
