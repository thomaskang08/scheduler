import axios from 'axios';
import { Agent, Client, CalendarEvent } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const formatDateTime = (dateTimeStr: string): string => {
    // Convert from HTML datetime-local format (YYYY-MM-DDTHH:mm) to ISO format with UTC timezone
    const date = new Date(dateTimeStr);
    return date.toISOString(); // This will include the 'Z' suffix indicating UTC
};

export const api = {
    getAgents: async (): Promise<Agent[]> => {
        const response = await axios.get(`${API_BASE_URL}/agents`);
        return response.data;
    },

    getCalendar: async (agentId: string): Promise<CalendarEvent[]> => {
        const response = await axios.get(`${API_BASE_URL}/calendar/${agentId}`);
        return response.data;
    },

    getClients: async (agentId: string): Promise<Client[]> => {
        const response = await axios.get(`${API_BASE_URL}/clients/${agentId}`);
        return response.data;
    },

    checkAvailability: async (agentId: string, dateTime: string): Promise<boolean> => {
        const response = await axios.get(`${API_BASE_URL}/availability/check/${agentId}`, {
            params: {
                datetime: formatDateTime(dateTime)
            }
        });
        return response.data.available;
    },

    findAvailableSlots: async (agentId: string, startDate: string, endDate: string): Promise<CalendarEvent[]> => {
        const response = await axios.get(`${API_BASE_URL}/availability/slots/${agentId}`, {
            params: {
                start_date: formatDateTime(startDate),
                end_date: formatDateTime(endDate)
            }
        });
        return response.data;
    },

    findBestWorkBlock: async (agentId: string, minDurationMinutes: number): Promise<CalendarEvent> => {
        const response = await axios.get(`${API_BASE_URL}/availability/best-block/${agentId}`, {
            params: {
                min_duration: minDurationMinutes
            }
        });
        return response.data;
    }
};
