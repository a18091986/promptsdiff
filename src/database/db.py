from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.schema import Base


engine = create_async_engine(url="postgresql+asyncpg://postgres:postgres@192.168.2.177:7777/test", echo=True)
async_session = async_sessionmaker(engine)


async def init_db():
    # await drop_tables()
    await create_tables()


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
