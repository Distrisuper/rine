import httpx
from fastapi import HTTPException

from app.config import get_settings


async def fetch_next_invoice(limit: int, host: int):
	settings = get_settings()
	if not settings.invoice_base_url:
		raise HTTPException(status_code=500, detail="INVOICE_BASE_URL is not configured")

	base_url = settings.invoice_base_url.rstrip("/")
	url = f"{base_url}/invoices/fifo/table/gm/print-queue"
	params = {"limit": limit, "host": host}

	async with httpx.AsyncClient() as client:
		response = await client.get(url, params=params)
		response.raise_for_status()
		return response.json()
