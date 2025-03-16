import React, { useState, useEffect } from 'react';
import { Typography, Skeleton, Paper } from '@mui/material';
import Calendar from './components/Calendar';
import ClientList from './components/ClientList';
import TimeRangeInput from './components/TimeRangeInput';
import AgentSelector from './components/AgentSelector';
import { api } from './services/api';
import { Agent, Client, CalendarEvent } from './types';
import './App.css';

function App() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [bestWorkBlock, setBestWorkBlock] = useState<CalendarEvent | null>(null);
  const [loadingInsight, setLoadingInsight] = useState(false);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const agentData = await api.getAgents();
        setAgents(agentData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading agents:', error);
        setLoading(false);
      }
    };
    loadAgents();
  }, []);

  useEffect(() => {
    const loadAgentData = async () => {
      if (selectedAgent) {
        try {
          setLoadingInsight(true);
          setBestWorkBlock(null);
          
          const [clientData, calendarData] = await Promise.all([
            api.getClients(selectedAgent.agent_id),
            api.getCalendar(selectedAgent.agent_id)
          ]);
          setClients(clientData);
          setEvents(calendarData);
          
          // Load best work block
          const workBlock = await api.findBestWorkBlock(selectedAgent.agent_id, 90);
          setBestWorkBlock(workBlock);
        } catch (error) {
          console.error('Error loading agent data:', error);
        } finally {
          setLoadingInsight(false);
        }
      } else {
        setClients([]);
        setEvents([]);
        setBestWorkBlock(null);
      }
    };
    loadAgentData();
  }, [selectedAgent]);

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    });
  };

  const renderScheduleInsight = () => {
    if (loadingInsight) {
      return (
        <div className="schedule-insight">
          <div className="time-range">
            <span className="label">Available:</span>
            <Skeleton variant="text" width={200} />
          </div>
          <div className="duration">
            <span className="label">Duration:</span>
            <Skeleton variant="text" width={100} />
          </div>
          <div className="analysis">
            <span className="label">Analysis:</span>
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="80%" />
          </div>
        </div>
      );
    }

    if (!selectedAgent) {
      return (
        <div className="schedule-insight">
          <Typography color="textSecondary" align="center">
            Select an agent to view schedule insights
          </Typography>
        </div>
      );
    }

    if (!bestWorkBlock) {
      return (
        <div className="schedule-insight">
          <Typography color="textSecondary" align="center">
            No available time blocks found
          </Typography>
        </div>
      );
    }

    return (
      <div className="schedule-insight">
        <div className="time-range">
          <span className="label">Available:</span>
          <span className="value">{formatDateTime(bestWorkBlock.start)} - {formatDateTime(bestWorkBlock.end)}</span>
        </div>
        <div className="duration">
          <span className="label">Duration:</span>
          <span className="value">{bestWorkBlock.duration_minutes} minutes</span>
        </div>
        <div className="analysis">
          <span className="label">Analysis:</span>
          <span className="value">{bestWorkBlock.description}</span>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="app-container">
      <div className="left-column">
        <div className="header">
          <h1>HouseWhisper Agent Dashboard</h1>
          <AgentSelector
            agents={agents}
            selectedAgent={selectedAgent}
            onSelect={setSelectedAgent}
          />
        </div>

        {selectedAgent && (
          <>
            <TimeRangeInput agentId={selectedAgent.agent_id} />
            <ClientList 
              clients={clients} 
              loading={loading} 
              selectedAgentName={selectedAgent?.name}
            />
          </>
        )}
      </div>

      <div className="right-column">
        <Paper elevation={3} sx={{ padding: 2, marginBottom: 2 }}>
          <Typography variant="h6" gutterBottom>
            Schedule Insight
          </Typography>
          {renderScheduleInsight()}
        </Paper>

        <Calendar 
          events={events} 
          loading={loading} 
          selectedAgentName={selectedAgent?.name}
        />
      </div>
    </div>
  );
}

export default App;
