# HouseWhisper Agent Dashboard

A modern real estate agent dashboard application that helps agents manage their schedules, clients, and find optimal work blocks using AI-powered insights.

## Features

- **Schedule Insights**: AI-powered analysis of the best available time blocks for focused work
- **Calendar Management**: Visual calendar interface for managing appointments and events
- **Client Management**: Track and manage client information and preferences
- **Availability Checker**: Check agent availability for specific time slots
- **Smart Scheduling**: Find available time slots within a date range

## Tech Stack

### Frontend
- React with TypeScript
- Material-UI for components
- FullCalendar for calendar visualization
- Axios for API communication

### Backend
- FastAPI (Python)
- OpenAI GPT-4 for schedule analysis
- Python-dotenv for environment management
- PyTZ for timezone handling

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python 3.12 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/thomaskang08/scheduler.git
cd scheduler
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

4. Set up the frontend:
```bash
cd frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd backend
python -m uvicorn web_app:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Features in Detail

### Schedule Insights
- AI-powered analysis of calendar patterns
- Identification of optimal work blocks
- Consideration of agent specialties and client needs
- Smart recommendations for focused work periods

### Calendar Features
- Week/Day view options
- Color-coded events
- Client meeting highlights
- Team meeting indicators

### Client Management
- Client status tracking (active/follow-up)
- Property preferences
- Price range tracking
- Contact history

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `GET /api/calendar/{agent_id}` - Get agent's calendar
- `GET /api/clients/{agent_id}` - Get agent's clients

### Availability
- `GET /api/availability/check/{agent_id}` - Check specific time availability
- `GET /api/availability/slots/{agent_id}` - Find available time slots
- `GET /api/availability/best-block/{agent_id}` - Get AI-recommended work block