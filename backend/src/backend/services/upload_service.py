from sqlalchemy.ext.asyncio import AsyncSession


async def get_uploads(_db: AsyncSession):
    return {"uploads": []}
