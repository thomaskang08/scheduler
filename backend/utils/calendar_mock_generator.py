import json
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import uuid
import os
import random
from pathlib import Path

def generate_mock_calendar(agent_id: str, num_events: int = 10) -> None:
    """Generate a mock calendar for an agent with random events."""
    cal = Calendar()
    cal.add('prodid', '-//HouseWhisper Calendar//')
    cal.add('version', '2.0')

    # Start from tomorrow
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tz = pytz.timezone('UTC')

    # Define different types of events and their durations
    event_types = [
        ("Client Meeting", 60),
        ("Property Viewing", 90),
        ("Team Sync", 30),
        ("Contract Review", 45),
        ("Market Analysis", 120),
        ("Client Follow-up", 30),
        ("Property Inspection", 120),
        ("Negotiation Meeting", 60)
    ]

    # Create a list of available days (next 14 days)
    available_days = [base_date + timedelta(days=i) for i in range(14)]
    
    # Generate events
    for i in range(num_events):
        event = Event()
        
        # Randomly select event type and duration
        event_type, duration = random.choice(event_types)
        
        # Randomly select a day
        event_day = random.choice(available_days)
        
        # Generate a random hour between 9 and 17 (9 AM to 5 PM)
        hour = random.randint(9, 16)
        minute = random.choice([0, 15, 30, 45])
        
        event_start = event_day.replace(hour=hour, minute=minute)
        event_end = event_start + timedelta(minutes=duration)

        event.add('summary', f"{event_type}")
        event.add('dtstart', tz.localize(event_start))
        event.add('dtend', tz.localize(event_end))
        event.add('description', f"{event_type} for agent {agent_id}")
        event.add('uid', str(uuid.uuid4()))

        cal.add_component(event)

    # Ensure the calendars directory exists
    calendars_dir = Path(__file__).parent.parent / 'data' / 'calendars'
    calendars_dir.mkdir(parents=True, exist_ok=True)

    # Write the calendar to a file
    calendar_path = calendars_dir / f'{agent_id}.ics'
    with open(calendar_path, 'wb') as f:
        f.write(cal.to_ical())

def generate_all_calendars():
    """Generate calendars for all agents in the mock data."""
    # Load mock data to get agent IDs
    mock_data_path = Path(__file__).parent.parent / 'data' / 'mock' / 'agents_clients.json'
    with open(mock_data_path, 'r') as f:
        mock_data = json.load(f)

    # Generate calendar for each agent with a random number of events
    for agent in mock_data['agents']:
        num_events = random.randint(8, 15)  # Random number of events per agent
        generate_mock_calendar(agent['agent_id'], num_events)

if __name__ == '__main__':
    generate_all_calendars() 