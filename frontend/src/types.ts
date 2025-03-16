export interface Agent {
    agent_id: string;
    name: string;
    specialty: string;
}

export interface Client {
    client_id: string;
    name: string;
    email: string;
    phone: string;
    status: 'active' | 'follow_up';
    preference: string;
    property_type: string;
    price_range: string;
    last_contact: string;
}

export interface CalendarEvent {
    summary: string;
    description: string;
    start: string;
    end: string;
    duration_minutes?: number;
}
