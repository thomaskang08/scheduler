from fastapi import FastAPI, HTTPException
from models.schemas import (
    AvailabilityRequest,
    AvailableSlotsRequest,
    WorkBlockRequest,
    TimeSlot
)
from services.availability_service import AvailabilityService
from storage.calendar_store import CalendarStore
from typing import List

app = FastAPI()
calendar_store = CalendarStore()
availability_service = AvailabilityService(calendar_store)

@app.post("/check-availability")
async def check_availability(request: AvailabilityRequest) -> bool:
    try:
        return availability_service.check_availability(
            request.agent_id,
            request.start_time,
            request.duration_minutes
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Agent calendar not found")

@app.post("/find-available-slots")
async def find_available_slots(request: AvailableSlotsRequest) -> List[TimeSlot]:
    try:
        return availability_service.find_available_slots(
            request.agent_id,
            request.time_ranges,
            request.duration_minutes,
            request.num_slots
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Agent calendar not found")

@app.post("/find-work-block")
async def find_work_block(request: WorkBlockRequest) -> TimeSlot:
    try:
        block = availability_service.find_best_work_block(
            request.agent_id,
            request.min_duration_minutes
        )
        if not block:
            raise HTTPException(status_code=404, detail="No suitable work block found")
        return block
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Agent calendar not found") 