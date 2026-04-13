import base64
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from infrastructure.api.routes import router
from infrastructure.api.exceptions import (
    validation_exception_handler,
    value_error_exception_handler,
)
from infrastructure.config import get_settings

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

# Global exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_exception_handler)

app.include_router(router)


@app.middleware("http")
async def admin_auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/admin") or request.url.path.startswith("/docs"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Admin"'},
                content={"detail": "Credenciales requeridas"}
            )

        credentials = base64.b64decode(auth_header[6:]).decode()
        username, password = credentials.split(":", 1)

        settings = get_settings()
        if not secrets.compare_digest(username, settings.admin_username):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Admin"'},
                content={"detail": "Credenciales inválidas"}
            )
        if not secrets.compare_digest(password, settings.admin_security_code):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Admin"'},
                content={"detail": "Credenciales inválidas"}
            )

    return await call_next(request)


app.mount("/admin", StaticFiles(directory="infrastructure/static/admin", html=True), name="admin")
