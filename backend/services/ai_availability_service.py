from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import pytz

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

class AIAvailabilityService:
    def __init__(self, calendar_store, agent_data_file: str = "data/mock/agents_clients.json"):
        self.calendar_store = calendar_store
        
        # Get API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
            
        self.openai_client = OpenAI(api_key=api_key)
        
        # Load agent data - fix path to be relative to backend directory
        agent_data_path = Path(__file__).resolve().parents[2] / "backend" / agent_data_file
        if not agent_data_path.exists():
            raise FileNotFoundError(f"Agent data file not found at {agent_data_path}")
            
        with open(agent_data_path, 'r') as f:
            self.agent_data = json.load(f)

    def _ensure_timezone_aware(self, dt):
        """Ensure datetime is timezone-aware, converting to UTC if it isn't"""
        if dt.tzinfo is None:
            return pytz.UTC.localize(dt)
        return dt.astimezone(pytz.UTC)

    def _get_agent_info(self, agent_id: str) -> Dict:
        """Get agent information including their clients and specialty"""
        for agent in self.agent_data['agents']:
            if agent['agent_id'] == agent_id:
                return agent
        raise ValueError(f"Agent {agent_id} not found")

    def _analyze_calendar_patterns(self, events: List[Dict], agent_info: Dict) -> Dict:
        """Analyze calendar patterns to understand agent's work habits"""
        patterns = {
            'meeting_times': [],
            'busy_days': set(),
            'avg_meeting_duration': 0,
            'client_meetings': 0,
            'team_meetings': 0
        }
        
        total_duration = timedelta()
        for event in events:
            # Ensure start and end times are timezone-aware
            start = self._ensure_timezone_aware(event['start'])
            end = self._ensure_timezone_aware(event['end'])
            
            patterns['meeting_times'].append(start.hour)
            patterns['busy_days'].add(start.strftime('%A'))
            
            duration = end - start
            total_duration += duration
            
            if 'Client:' in event.get('description', ''):
                patterns['client_meetings'] += 1
            elif 'Team' in event.get('summary', ''):
                patterns['team_meetings'] += 1
        
        if events:
            patterns['avg_meeting_duration'] = (total_duration / len(events)).total_seconds() / 60
        
        return patterns

    def _format_work_block_prompt(self, 
                                available_blocks: List[Dict], 
                                patterns: Dict,
                                agent_info: Dict) -> str:
        """Format the prompt for OpenAI to analyze work blocks"""
        blocks_text = []
        for block in available_blocks:
            duration = (block['end'] - block['start']).total_seconds() / 3600  # hours
            blocks_text.append(
                f"- {block['start'].strftime('%A %I:%M %p')} to {block['end'].strftime('%I:%M %p')} "
                f"(Duration: {duration:.1f} hours)"
            )
        
        active_clients = sum(1 for client in agent_info['clients'] if client['status'] == 'active')
        follow_up_clients = sum(1 for client in agent_info['clients'] if client['status'] == 'follow_up')
        
        prompt = f"""
As an AI assistant for a real estate agent, analyze these available work blocks and recommend the best one:

Agent Profile:
- Specialty: {agent_info['specialty']}
- Active Clients: {active_clients}
- Clients Needing Follow-up: {follow_up_clients}

Available Time Blocks:
{chr(10).join(blocks_text)}

Calendar Patterns:
- Most meetings occur between: {min(patterns['meeting_times'])}:00 - {max(patterns['meeting_times'])}:00
- Average meeting duration: {patterns['avg_meeting_duration']:.0f} minutes
- Client meetings this week: {patterns['client_meetings']}
- Team meetings this week: {patterns['team_meetings']}

Consider:
1. Length of the block (longer blocks better for deep work)
2. Time of day (morning often better for focused work)
3. Day of week (consider patterns in existing meetings)
4. Client follow-up needs
5. Agent's specialty and typical work patterns

Which block would be most productive for focused work and why?
"""
        return prompt

    def find_best_work_block(self, 
                           agent_id: str, 
                           min_duration_minutes: int = 60) -> Optional[Dict]:
        """
        Find the best work block using AI analysis of calendar patterns and agent context
        """
        # Get agent information
        agent_info = self._get_agent_info(agent_id)
        
        # Get calendar events for the next 7 days
        start_time = self._ensure_timezone_aware(datetime.now())
        end_time = self._ensure_timezone_aware(start_time + timedelta(days=7))
        events = self.calendar_store.get_events(agent_id, start_time, end_time)
        
        # Analyze calendar patterns
        patterns = self._analyze_calendar_patterns(events, agent_info)
        
        # Find available blocks
        available_blocks = []
        current_time = start_time
        
        # Sort events by start time
        events.sort(key=lambda x: x['start'])
        
        for event in events:
            # Ensure event times are timezone-aware
            event_start = self._ensure_timezone_aware(event['start'])
            event_end = self._ensure_timezone_aware(event['end'])
            
            gap = event_start - current_time
            gap_minutes = gap.total_seconds() / 60
            
            if gap_minutes >= min_duration_minutes:
                available_blocks.append({
                    'start': current_time,
                    'end': event_start,
                    'duration_minutes': int(gap_minutes)
                })
            current_time = event_end
        
        if not available_blocks:
            return None
            
        # Use OpenAI to analyze and choose the best block
        prompt = self._format_work_block_prompt(available_blocks, patterns, agent_info)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping real estate agents optimize their work schedule."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Parse the response to identify the recommended block
        response_text = response.choices[0].message.content.lower()
        
        # Find the block that best matches the AI's recommendation
        for block in available_blocks:
            block_desc = f"{block['start'].strftime('%A %I:%M %p')}".lower()
            if block_desc in response_text:
                return {
                    'start': block['start'],
                    'end': block['end'],
                    'duration_minutes': block['duration_minutes'],
                    'ai_reasoning': response.choices[0].message.content
                }
        
        # If no specific block was identified in the response, return the longest available block
        longest_block = max(available_blocks, key=lambda x: x['duration_minutes'])
        return {
            'start': longest_block['start'],
            'end': longest_block['end'],
            'duration_minutes': longest_block['duration_minutes'],
            'ai_reasoning': "Selected the longest available time block for maximum productivity."
        } 