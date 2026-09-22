from datetime import date, datetime

from pydantic import BaseModel, Field


class AvailabilityRequest(BaseModel):
    date: date


class AvailabilitySlot(BaseModel):
    slot_id: int
    start_time: datetime
    end_time: datetime
    spoken_label: str


class BookingRequest(BaseModel):
    slot_id: int
    caller_name: str = Field(min_length=1, max_length=100)
    caller_phone: str = Field(min_length=7, max_length=20)


class BookingConfirmation(BaseModel):
    confirmation_code: str = Field(min_length=6, max_length=10)
    spoken_confirmation: str


class BookingDetails(BaseModel):
    confirmation_code: str
    caller_name: str
    caller_phone: str
    slot_id: int

    model_config = {"from_attributes": True}
