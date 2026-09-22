import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.database import AsyncSessionLocal
from app.models import Provider, Slot

PROVIDER_TZ = ZoneInfo("Africa/Accra")


async def seed():
    async with AsyncSessionLocal() as session:
        provider = Provider(name="Dr. Mensah")
        session.add(provider)
        await session.flush()  # assigns provider.id without fully committing yet

        tomorrow_9am = (
            datetime.now(PROVIDER_TZ)
            .replace(hour=9, minute=0, second=0, microsecond=0)
            + timedelta(days=1)
        )

        for i in range(5):
            start = tomorrow_9am + timedelta(hours=i)
            end = start + timedelta(minutes=30)
            session.add(Slot(provider_id=provider.id, start_time=start, end_time=end))

        await session.commit()

    print("Seeded 1 provider and 5 slots for tomorrow.")


if __name__ == "__main__":
    asyncio.run(seed())