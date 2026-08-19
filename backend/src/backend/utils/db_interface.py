import logging
import os
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from backend.utils.exceptions import DBConnectionError

logger = logging.getLogger(__name__)
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

encoded_password = urllib.parse.quote_plus(DB_PASSWORD or "")

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# echo=False to avoid SQL logging; use sqlalchemy.engine logger level for additional control
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
    pool_size=3,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    logger.debug("get_db: opening DB session")
    async with SessionLocal() as session:
        logger.debug("get_db: yielding session")
        yield session


async def test_connection(db: AsyncSession):
    try:
        result = await db.execute(select(1))
        _ = result.scalar_one()
        logger.debug("Database connection is working.")
    except Exception as e:
        logger.warning("SQLAlchemy error occurred: %s", e)
        raise DBConnectionError from e

async def test_check():
    pass
