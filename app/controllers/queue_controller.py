from app.services.queue_service import fetch_next_invoice


class QueueController:
    @staticmethod
    async def next_invoice(limit: int, host: int):
        return await fetch_next_invoice(limit=limit, host=host)
