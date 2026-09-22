from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.schemas import (
    AvailabilityRequest,
    AvailabilitySlot,
    BookingConfirmation,
    BookingDetails,
    BookingRequest,
)
from app.services import booking_service
from app.services.booking_service import SlotAlreadyBookedError

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/get_today")
async def get_today():
    today = booking_service.get_today()
    return {
        "today": today.isoformat(),
        "spoken": today.strftime("Today is %A, %B %-d"),
    }


@router.post("/check_availability", response_model=list[AvailabilitySlot])
async def check_availability(
    request: AvailabilityRequest,
    db: AsyncSession = Depends(get_db),
):
    slots = await booking_service.check_availability(db, request.date)
    return slots  # an empty list is a valid, non-error answer — not everything is a 404


@router.post("/book_slot", response_model=BookingConfirmation)
async def book_slot(
    request: BookingRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.book_slot(
            db,
            slot_id=request.slot_id,
            caller_name=request.caller_name,
            caller_phone=request.caller_phone,
        )
    except SlotAlreadyBookedError:
        raise HTTPException(
            status_code=409,
            detail="That slot was just taken, would you like another time?",
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return booking


class ConfirmBookingRequest(BaseModel):
    confirmation_code: str


@router.post("/confirm_booking", response_model=BookingDetails)
async def confirm_booking(
    request: ConfirmBookingRequest,
    db: AsyncSession = Depends(get_db),
):
    booking = await booking_service.get_booking(db, request.confirmation_code)
    if booking is None:
        raise HTTPException(status_code=404, detail="No booking found with that confirmation code.")
    return booking