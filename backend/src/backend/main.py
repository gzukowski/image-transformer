import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from uvicorn import Config, Server

from backend.utils.db_interface import get_db, test_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("log/app.log", mode="a", encoding="utf-8")
    ]
)
@asynccontextmanager
async def lifespan_context_manager(_):
    logger = logging.getLogger(__name__)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpx._client").setLevel(logging.WARNING)

    try:
        async for db_session in get_db():
            logger.info("Starting database connection test...")
            await test_connection(db_session)
            logger.info("Database connection is successful!")

        FastAPICache.init(InMemoryBackend())
        logger.info("✅ InMemory cache initialized for development")

        yield

    except Exception:
        logger.exception("Failed to connect to the database")
        raise

app = FastAPI(
    lifespan=lifespan_context_manager,
    title="image-transformer-backend",
    description="restful service for image-transformer",
    version="1.0.0",
    logger=logging.getLogger("server_logger"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def prod():
    config = Config(app="backend.main:app", log_level="info")
    server = Server(config=config)
    server.run()

def dev():
    config = Config(app="backend.main:app", log_level="info", reload=True, reload_dirs=["src"])
    server = Server(config=config)
    server.run()
