import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import Slot, Booking
from app.schemas import AvailabilitySlot, BookingConfirmation

PROVIDER_TZ = ZoneInfo("Africa/Accra")


class SlotAlreadyBookedError(Exception):
    pass


def get_today() -> date:
    return datetime.now(PROVIDER_TZ).date()


def _to_spoken_label(dt: datetime) -> str:
    local_dt = dt.astimezone(PROVIDER_TZ)
    return local_dt.strftime("%A, %B %-d at %-I:%M %p")


def _generate_confirmation_code(length: int = 6) -> str:
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O or 1/I — unambiguous spoken aloud
    return "".join(random.choices(alphabet, k=length))


async def check_availability(db: AsyncSession, target_date: date) -> list[AvailabilitySlot]:
    result = await db.execute(
        select(Slot).where(
            Slot.start_time >= datetime.combine(target_date, datetime.min.time(), PROVIDER_TZ),
            Slot.start_time < datetime.combine(target_date, datetime.max.time(), PROVIDER_TZ),
            Slot.is_booked == False,  # noqa: E712
        )
    )
    slots = result.scalars().all()

    return [
        AvailabilitySlot(
            slot_id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            spoken_label=_to_spoken_label(slot.start_time),
        )
        for slot in slots
    ]


async def book_slot(
    db: AsyncSession, slot_id: int, caller_name: str, caller_phone: str
) -> BookingConfirmation:
    normalized_phone = "".join(caller_phone.split())
    digits = normalized_phone[1:] if normalized_phone.startswith("+") else normalized_phone
    if not digits.isdigit() or not 7 <= len(digits) <= 15:
        raise ValueError("Caller phone must contain 7 to 15 digits")

    async with db.begin():
        result = await db.execute(
            select(Slot).where(Slot.id == slot_id).with_for_update()
        )
        slot = result.scalar_one_or_none()

        if slot is None:
            raise ValueError(f"No slot with id {slot_id}")
        if slot.is_booked:
            raise SlotAlreadyBookedError(f"Slot {slot_id} is already booked")

        slot.is_booked = True
        booking = Booking(
            slot_id=slot.id,
            caller_name=caller_name,
            caller_phone=normalized_phone,
            confirmation_code=_generate_confirmation_code(),
        )
        db.add(booking)

        try:
            await db.flush()
        except IntegrityError:
            raise SlotAlreadyBookedError(f"Slot {slot_id} is already booked")

    return BookingConfirmation(
        confirmation_code=booking.confirmation_code,
        spoken_confirmation=(
            f"You're booked for {_to_spoken_label(slot.start_time)}. "
            f"Your confirmation code is {booking.confirmation_code}."
        ),
    )


async def get_booking(db: AsyncSession, confirmation_code: str) -> Booking | None:
    result = await db.execute(
        select(Booking).where(Booking.confirmation_code == confirmation_code)
    )
    return result.scalar_one_or_none()