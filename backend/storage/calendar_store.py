from icalendar import Calendar
from datetime import datetime, timedelta
import os
from typing import Dict, List
from pathlib import Path
from utils.calendar_mock_generator import generate_mock_calendar
import pytz

class CalendarStore:
    def __init__(self):
        self.calendars_dir = Path(__file__).parent.parent / 'data' / 'calendars'
        self.calendars_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, List[Dict]] = {}
        self.timezone = pytz.UTC  # Use UTC as our standard timezone

    def _ensure_calendar_exists(self, agent_id: str) -> None:
        """Ensure calendar file exists for the agent, create if it doesn't"""
        calendar_path = self.calendars_dir / f'{agent_id}.ics'
        if not calendar_path.exists():
            generate_mock_calendar(agent_id)

    def _make_timezone_aware(self, dt: datetime) -> datetime:
        """Convert naive datetime to timezone-aware"""
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt.astimezone(self.timezone)

    def get_events(self, agent_id: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get events for an agent within the specified time range"""
        self._ensure_calendar_exists(agent_id)
        
        # Make input times timezone-aware if they aren't already
        start_time = self._make_timezone_aware(start_time)
        end_time = self._make_timezone_aware(end_time)
        
        if agent_id not in self._cache:
            calendar_path = self.calendars_dir / f'{agent_id}.ics'
            try:
                with open(calendar_path, 'rb') as f:
                    cal = Calendar.from_ical(f.read())
                    events = []
                    for component in cal.walk('VEVENT'):
                        event_start = component.get('dtstart').dt
                        event_end = component.get('dtend').dt
                        
                        # Convert to datetime if date
                        if not isinstance(event_start, datetime):
                            event_start = datetime.combine(event_start, datetime.min.time())
                        if not isinstance(event_end, datetime):
                            event_end = datetime.combine(event_end, datetime.max.time())
                        
                        # Make timezone-aware
                        event_start = self._make_timezone_aware(event_start)
                        event_end = self._make_timezone_aware(event_end)
                        
                        events.append({
                            'start': event_start,
                            'end': event_end,
                            'summary': str(component.get('summary')),
                            'description': str(component.get('description', ''))
                        })
                    self._cache[agent_id] = events
            except Exception as e:
                print(f"Error loading calendar for agent {agent_id}: {str(e)}")
                return []

        # Filter events within the time range
        return [
            event for event in self._cache[agent_id]
            if not (event['end'] <= start_time or event['start'] >= end_time)
        ] 