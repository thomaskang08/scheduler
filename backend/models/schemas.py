from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
import pytz

def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware"""
    if dt.tzinfo is None:
        return pytz.UTC.localize(dt)
    return dt.astimezone(pytz.UTC)

class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @validator('start', 'end')
    def ensure_timezone(cls, v):
        return ensure_timezone_aware(v)

    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('end time must be after start time')
        return v

class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    description: Optional[str] = None

    @validator('start', 'end')
    def ensure_timezone(cls, v):
        return ensure_timezone_aware(v)

    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('end time must be after start time')
        return v

class Agent(BaseModel):
    agent_id: str
    name: str
    specialty: str
    clients: List[dict] = []

class Client(BaseModel):
    client_id: str
    name: str
    email: str
    phone: str
    status: str

class AvailabilityRequest(BaseModel):
    agent_id: str
    start_time: datetime
    duration_minutes: int

    @validator('start_time')
    def ensure_timezone(cls, v):
        return ensure_timezone_aware(v)

class AvailableSlotsRequest(BaseModel):
    agent_id: str
    time_ranges: List[TimeRange]
    duration_minutes: int
    num_slots: int
