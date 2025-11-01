from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["example"])


@router.get("/example/", status_code=status.HTTP_200_OK)
async def read_example_with_slash(request: Request):
    """Example endpoint that returns a greeting message."""
    client_host = request.client.host
    logger.info(f"Received request from {client_host}")
    return {"message": "Hello, this is an example endpoint!", "client_ip": client_host}


@router.get("/example", status_code=status.HTTP_302_FOUND)
async def read_example_no_slash(request: Request):
    """Redirect from /example to /example/"""
    return RedirectResponse(url="/api/v1/example/", status_code=302)
