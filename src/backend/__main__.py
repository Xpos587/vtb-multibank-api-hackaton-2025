if __name__ == "__main__":
    from granian.server import Server as Granian
    from granian.constants import Interfaces, Loops

    from .core.config import settings
    from .core.logging import get_logger

    logger = get_logger(__name__)

    logger.info(
        f"🚀 Starting {settings.app.name} on {settings.app.host}:{settings.app.port}"
    )

    server = Granian(
        target="src.backend.app:app",
        interface=Interfaces.ASGI,
        loop=Loops.uvloop,
        address=settings.app.host,
        port=settings.app.port,
    )
    server.serve()
