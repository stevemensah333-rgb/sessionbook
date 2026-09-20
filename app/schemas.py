from pydantic import BaseModel, Field
from datetime import date

class AvailabilityRequest(BaseModel):
    date: date

class AvailabilitySlot(BaseModel):
    slot_id: int 
    start_time: str
    end_time: str
    spoken_label: str

class BookingRequest(BaseModel):
    slot_id: int
    caller_name: str = Field(min_length=1, max_length=100)
    caller_phone: str = Field(pattern=r"^\+?[0-9]{7,15}$")

class BookingConfirmation(BaseModel):
    confirmation_code: str = Field(min_length=6, max_length=10)
    spoken_confirmation: str
