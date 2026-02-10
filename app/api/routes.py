# API routes mínimas
from fastapi import APIRouter
from app.controllers.hello_controller import HelloController

router = APIRouter()

@router.get("/")
async def root():
    return HelloController.root()

@router.get("/health")
async def health():
    return HelloController.health()
