from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from infrastructure.presentation.api.routes import router

app = FastAPI(
    title="RINE Print Manager API",
    description="API para templates (remito PDF, etiqueta ZPL) y monitoreo de impresoras vía CUPS.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Raíz y estado del servicio"},
        {"name": "PrintJobs", "description": "Crear y gestionar trabajos de impresión"},
        {"name": "Printers", "description": "Estado de impresoras (CUPS) y envío de trabajos"},
        {"name": "Templates", "description": "Prueba de templates remito (PDF) y etiqueta (ZPL)"},
    ],
)
app.include_router(router)

# Serve admin dashboard at /admin
app.mount("/admin", StaticFiles(directory="infrastructure/static/admin", html=True), name="admin")
