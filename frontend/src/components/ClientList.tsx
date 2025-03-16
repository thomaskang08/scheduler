import React from 'react';
import { Card, CardContent, Typography, Stack, Paper, Skeleton } from '@mui/material';
import { Client } from '../types';

interface ClientListProps {
  clients: Client[];
  loading?: boolean;
  selectedAgentName?: string;
}

const ClientList: React.FC<ClientListProps> = ({ clients, loading = false, selectedAgentName }) => {
  if (loading) {
    return (
      <Paper elevation={3} sx={{ padding: 2, height: '400px', overflowY: 'auto' }}>
        <Stack spacing={2}>
          {[1, 2, 3].map((index) => (
            <Card key={index} variant="outlined">
              <CardContent>
                <Skeleton variant="text" width="60%" height={32} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="40%" sx={{ mb: 1 }} />
                <Skeleton variant="text" width="70%" sx={{ mb: 1 }} />
                <Skeleton variant="text" width="50%" sx={{ mb: 1 }} />
                <Skeleton variant="text" width="45%" />
              </CardContent>
            </Card>
          ))}
        </Stack>
      </Paper>
    );
  }

  if (!selectedAgentName) {
    return (
      <Paper elevation={3} sx={{ 
        padding: 2, 
        height: '400px', 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography color="textSecondary">
          Select an agent to view their clients
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ padding: 2, height: '400px', overflowY: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        {selectedAgentName}'s Clients
      </Typography>
      <Stack spacing={2}>
        {clients.length === 0 ? (
          <Typography color="textSecondary" align="center">
            No clients found
          </Typography>
        ) : (
          clients.map((client) => (
            <Card key={client.client_id} variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {client.name}
                </Typography>
                <Typography 
                  color={client.status === 'active' ? 'success.main' : 'warning.main'}
                  gutterBottom
                >
                  Status: {client.status}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Preference: {client.preference}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Property Type: {client.property_type}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Price Range: {client.price_range}
                </Typography>
                <Typography variant="body2">
                  Last Contact: {client.last_contact}
                </Typography>
              </CardContent>
            </Card>
          ))
        )}
      </Stack>
    </Paper>
  );
};

export default ClientList;
