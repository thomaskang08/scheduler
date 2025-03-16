from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import uuid

class CalendarGenerator:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.calendar = Calendar()
        self.calendar.add('prodid', f'-//HouseWhisper//Agent-{agent_id}//')
        self.calendar.add('version', '2.0')

    def add_event(self, summary: str, start_time: datetime, duration_minutes: int):
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start_time)
        event.add('dtend', start_time + timedelta(minutes=duration_minutes))
        event.add('uid', str(uuid.uuid4()))
        self.calendar.add_component(event)

    def generate_test_calendar(self):
        # Generate a week's worth of test data
        tz = pytz.timezone('America/Los_Angeles')
        base_date = datetime.now(tz).replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Regular meetings during work hours
        self.add_event("Morning Team Sync", base_date, 30)
        self.add_event("Client Meeting", base_date.replace(hour=14), 60)
        
        # Back-to-back meetings
        tomorrow = base_date + timedelta(days=1)
        self.add_event("Property Viewing", tomorrow.replace(hour=10), 60)
        self.add_event("Contract Review", tomorrow.replace(hour=11), 60)
        
        # All-day event
        day_after = base_date + timedelta(days=2)
        event = Event()
        event.add('summary', "Training Day")
        event.add('dtstart', day_after.date())
        event.add('dtend', (day_after + timedelta(days=1)).date())
        event.add('uid', str(uuid.uuid4()))
        self.calendar.add_component(event)

    def save_to_file(self, filename: str):
        with open(filename, 'wb') as f:
            f.write(self.calendar.to_ical()) 