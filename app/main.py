from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models import Provider, Slot
from app.routers import tools


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        if await session.scalar(select(Slot.id).limit(1)) is None:
            provider = Provider(name="SessionBook Provider")
            session.add(provider)
            await session.flush()
            timezone = ZoneInfo("Africa/Accra")
            first_day = datetime.now(timezone).date()
            for day_offset in range(14):
                start_of_day = datetime.combine(
                    first_day + timedelta(days=day_offset),
                    datetime.min.time(),
                    timezone,
                ).replace(hour=9)
                for hour_offset in range(5):
                    start = start_of_day + timedelta(hours=hour_offset)
                    session.add(
                        Slot(
                            provider_id=provider.id,
                            start_time=start,
                            end_time=start + timedelta(minutes=30),
                        )
                    )
            await session.commit()
    yield
    await engine.dispose()


app = FastAPI(title="SessionBook", lifespan=lifespan)
app.include_router(tools.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
