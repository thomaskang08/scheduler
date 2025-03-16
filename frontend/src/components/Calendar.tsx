import React from 'react';
import { Paper, Typography, Skeleton } from '@mui/material';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { CalendarEvent } from '../types';

interface CalendarProps {
  events: CalendarEvent[];
  loading?: boolean;
  selectedAgentName?: string;
}

const Calendar: React.FC<CalendarProps> = ({ events, loading = false, selectedAgentName }) => {
  const formattedEvents = events.map(event => ({
    title: event.summary,
    start: event.start,
    end: event.end,
    extendedProps: {
      description: event.description
    },
    backgroundColor: event.description?.includes('Client:') ? '#4CAF50' : '#2196F3'
  }));

  if (loading) {
    return (
      <Paper elevation={3} sx={{ 
        padding: 2, 
        height: '600px',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <Skeleton variant="rectangular" height={40} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={520} />
      </Paper>
    );
  }

  if (!selectedAgentName) {
    return (
      <Paper elevation={3} sx={{ 
        padding: 2, 
        height: '600px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography color="textSecondary">
          Select an agent to view their calendar
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ 
      padding: 2, 
      height: '600px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Typography variant="h6" gutterBottom>
        {selectedAgentName}'s Calendar
      </Typography>
      <div style={{ flex: 1, minHeight: 0 }}>
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
          }}
          slotMinTime="08:00:00"
          slotMaxTime="20:00:00"
          events={formattedEvents}
          eventClick={(info) => {
            alert(info.event.extendedProps.description || info.event.title);
          }}
          height="100%"
        />
      </div>
    </Paper>
  );
};

export default Calendar;
