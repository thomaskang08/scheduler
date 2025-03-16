from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict
from pathlib import Path
import pytz
from services.availability_service import AvailabilityService
from services.ai_availability_service import AIAvailabilityService
from storage.calendar_store import CalendarStore
from utils.calendar_mock_generator import generate_all_calendars
from models.schemas import TimeRange, TimeSlot

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calendar_store = CalendarStore()
availability_service = AvailabilityService(calendar_store)
ai_availability_service = AIAvailabilityService(calendar_store)

# Load mock data
data_path = Path(__file__).parent / "data/mock/agents_clients.json"
with open(data_path, "r") as f:
    AGENTS_DATA = json.load(f)

# Ensure calendar data exists
generate_all_calendars()

def parse_datetime(datetime_str: str) -> datetime:
    """Parse ISO format datetime string and ensure it's timezone-aware"""
    dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt

def make_timezone_aware(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware"""
    if dt.tzinfo is None:
        return pytz.UTC.localize(dt)
    return dt.astimezone(pytz.UTC)

class CalendarService:
    @staticmethod
    def load_calendar(agent_id: str) -> List[Dict]:
        try:
            calendar_path = Path(__file__).parent / f"data/calendars/{agent_id}.ics"
            if not os.path.exists(calendar_path):
                return []
                
            from icalendar import Calendar
            
            events = []
            with open(calendar_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
                for component in cal.walk('VEVENT'):
                    event_start = component.get('dtstart').dt
                    event_end = component.get('dtend').dt
                    
                    # Convert to datetime if date
                    if not isinstance(event_start, datetime):
                        event_start = datetime.combine(event_start, datetime.min.time())
                    if not isinstance(event_end, datetime):
                        event_end = datetime.combine(event_end, datetime.max.time())
                    
                    # Make timezone-aware
                    event_start = make_timezone_aware(event_start)
                    event_end = make_timezone_aware(event_end)
                    
                    event = {
                        'summary': str(component.get('summary')),
                        'description': str(component.get('description', '')),
                        'start': event_start.isoformat(),
                        'end': event_end.isoformat()
                    }
                    events.append(event)
            return events
        except Exception as e:
            print(f"Error loading calendar for agent {agent_id}: {str(e)}")
            return []

@app.get("/")
async def read_root():
    return FileResponse(str(static_path / "index.html"))

@app.get("/api/agents")
async def get_agents():
    return [
        {
            "agent_id": agent["agent_id"],
            "name": agent["name"],
            "specialty": agent["specialty"]
        }
        for agent in AGENTS_DATA["agents"]
    ]

@app.get("/api/calendar/{agent_id}")
async def get_calendar(agent_id: str):
    events = CalendarService.load_calendar(agent_id)
    if not events:
        return []
    return events

@app.get("/api/clients/{agent_id}")
async def get_clients(agent_id: str):
    for agent in AGENTS_DATA["agents"]:
        if agent["agent_id"] == agent_id:
            return agent["clients"]
    raise HTTPException(status_code=404, detail="Agent not found")

@app.get("/api/availability/check/{agent_id}")
async def check_availability(
    agent_id: str,
    datetime_str: str = Query(..., alias="datetime", description="The datetime to check availability for")
):
    try:
        check_time = parse_datetime(datetime_str)
        is_available = availability_service.check_availability(agent_id, check_time, 60)  # Check for 1-hour slot
        return {"available": is_available}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/availability/slots/{agent_id}")
async def find_available_slots(
    agent_id: str,
    start_date: str = Query(..., description="Start datetime for the range"),
    end_date: str = Query(..., description="End datetime for the range")
):
    try:
        start_time = parse_datetime(start_date)
        end_time = parse_datetime(end_date)
        
        time_range = TimeRange(start=start_time, end=end_time)
        
        available_slots = availability_service.find_available_slots(
            agent_id=agent_id,
            time_ranges=[time_range],
            duration_minutes=60,  # 1-hour slots
            num_slots=10  # Return up to 10 slots
        )
        
        return [
            {
                "summary": "Available Slot",
                "description": "This time slot is available for booking",
                "start": slot.start.isoformat(),
                "end": slot.end.isoformat()
            }
            for slot in available_slots
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/availability/best-block/{agent_id}")
async def find_best_work_block(
    agent_id: str,
    min_duration: int = Query(90, description="Minimum duration in minutes for the work block")
):
    try:
        best_block = ai_availability_service.find_best_work_block(agent_id, min_duration)
        if best_block:
            return {
                "summary": "Schedule Insight",
                "description": best_block.get('ai_reasoning', 'Optimal time block for focused work'),
                "start": best_block['start'].isoformat(),
                "end": best_block['end'].isoformat(),
                "duration_minutes": best_block['duration_minutes']
            }
        raise HTTPException(status_code=404, detail="No suitable work block found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 