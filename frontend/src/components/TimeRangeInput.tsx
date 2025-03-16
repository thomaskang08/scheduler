import React, { useState } from 'react';
import { TextField, Button, Box, Stack, Paper, Typography, InputLabel, FormControl } from '@mui/material';
import { api } from '../services/api';

interface TimeRangeInputProps {
  agentId: string;
}

const TimeRangeInput: React.FC<TimeRangeInputProps> = ({ agentId }) => {
  const [checkDateTime, setCheckDateTime] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCheckAvailability = async () => {
    if (!checkDateTime) return;
    setLoading(true);
    try {
      const isAvailable = await api.checkAvailability(agentId, checkDateTime);
      alert(isAvailable ? 'Time slot is available!' : 'Time slot is not available');
    } catch (error) {
      console.error('Error checking availability:', error);
      alert('Error checking availability');
    } finally {
      setLoading(false);
    }
  };

  const handleFindSlots = async () => {
    if (!startDate || !endDate) return;
    setLoading(true);
    try {
      const slots = await api.findAvailableSlots(agentId, startDate, endDate);
      alert(`Found ${slots.length} available slots`);
    } catch (error) {
      console.error('Error finding slots:', error);
      alert('Error finding available slots');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ padding: 2 }}>
      <Stack spacing={3}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Check Single Time
          </Typography>
          <Stack spacing={2}>
            <FormControl fullWidth>
              <InputLabel shrink htmlFor="check-datetime">
                Select Date & Time
              </InputLabel>
              <TextField
                id="check-datetime"
                type="datetime-local"
                value={checkDateTime}
                onChange={(e) => setCheckDateTime(e.target.value)}
                fullWidth
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{ mt: 2 }}
              />
            </FormControl>
            <Button
              variant="contained"
              onClick={handleCheckAvailability}
              disabled={loading || !checkDateTime}
              fullWidth
            >
              Check Availability
            </Button>
          </Stack>
        </Box>

        <Box>
          <Typography variant="h6" gutterBottom>
            Find Available Slots
          </Typography>
          <Stack spacing={2}>
            <FormControl fullWidth>
              <InputLabel shrink htmlFor="start-datetime">
                Start Date & Time
              </InputLabel>
              <TextField
                id="start-datetime"
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                fullWidth
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{ mt: 2 }}
              />
            </FormControl>
            <FormControl fullWidth>
              <InputLabel shrink htmlFor="end-datetime">
                End Date & Time
              </InputLabel>
              <TextField
                id="end-datetime"
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                fullWidth
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{ mt: 2 }}
              />
            </FormControl>
            <Button
              variant="contained"
              onClick={handleFindSlots}
              disabled={loading || !startDate || !endDate}
              fullWidth
            >
              Find Available Slots
            </Button>
          </Stack>
        </Box>
      </Stack>
    </Paper>
  );
};

export default TimeRangeInput;
