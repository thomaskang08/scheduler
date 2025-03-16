from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from storage.calendar_store import CalendarStore
from models.schemas import TimeRange, TimeSlot

class AvailabilityService:
    def __init__(self, calendar_store: CalendarStore):
        self.calendar_store = calendar_store
        self.timezone = pytz.UTC

    def _make_timezone_aware(self, dt: datetime) -> datetime:
        """Ensure a datetime is timezone-aware"""
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt.astimezone(self.timezone)

    def check_availability(self, agent_id: str, check_time: datetime, duration_minutes: int) -> bool:
        """
        Check if an agent is available at a specific time for a given duration
        """
        # Ensure timezone-aware
        check_time = self._make_timezone_aware(check_time)
        
        # Get events that overlap with the time range we're checking
        start_time = check_time
        end_time = check_time + timedelta(minutes=duration_minutes)
        
        events = self.calendar_store.get_events(agent_id, start_time, end_time)
        
        # If there are any events during this time, the agent is not available
        return len(events) == 0

    def find_available_slots(
        self,
        agent_id: str,
        time_ranges: List[TimeRange],
        duration_minutes: int,
        num_slots: int = 5
    ) -> List[TimeSlot]:
        """
        Find available time slots for an agent within the given time ranges
        """
        available_slots = []
        
        for time_range in time_ranges:
            # Ensure timezone-aware
            current_time = self._make_timezone_aware(time_range.start)
            end_time = self._make_timezone_aware(time_range.end)
            
            slot_duration = timedelta(minutes=duration_minutes)
            
            while current_time + slot_duration <= end_time and len(available_slots) < num_slots:
                if self.check_availability(agent_id, current_time, duration_minutes):
                    slot = TimeSlot(
                        start=current_time,
                        end=current_time + slot_duration,
                        description=f"Available {duration_minutes} minute slot"
                    )
                    available_slots.append(slot)
                
                # Move to next potential slot (try every 30 minutes)
                current_time += timedelta(minutes=30)
        
        return available_slots

    def find_best_work_block(self, agent_id: str, min_duration_minutes: int) -> Optional[TimeSlot]:
        # Look for blocks in the next 7 days
        start_time = self._make_timezone_aware(datetime.now())
        end_time = start_time + timedelta(days=7)
        events = self.calendar_store.get_events(agent_id, start_time, end_time)
        
        # Sort events by start time
        events.sort(key=lambda x: x['start'])
        
        best_block = None
        max_duration = timedelta(minutes=0)
        
        # Check gaps between events
        current_time = start_time
        for event in events:
            gap = event['start'] - current_time
            if gap >= timedelta(minutes=min_duration_minutes):
                if gap > max_duration:
                    max_duration = gap
                    best_block = TimeSlot(start=current_time, end=event['start'])
            current_time = event['end']
        
        return best_block 