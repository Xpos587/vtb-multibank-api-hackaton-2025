from fastapi import APIRouter

from .endpoints.example import router as example_router

router = APIRouter(prefix="/v1")

router.include_router(example_router, tags=["example"])
