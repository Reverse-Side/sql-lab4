import logging
from src.database import Base, engine
from src.load_models import load_all_orm_models

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

load_all_orm_models()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    log.info("✅ Базу даних і таблиці створено успішно.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
