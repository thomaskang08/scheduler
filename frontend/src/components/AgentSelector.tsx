import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Agent } from '../types';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onSelect: (agent: Agent | null) => void;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onSelect,
}) => {
  return (
    <FormControl fullWidth>
      <InputLabel>Select Agent</InputLabel>
      <Select
        value={selectedAgent?.agent_id || ''}
        label="Select Agent"
        onChange={(e) => {
          const agent = agents.find(a => a.agent_id === e.target.value);
          onSelect(agent || null);
        }}
      >
        <MenuItem value="">
          <em>None</em>
        </MenuItem>
        {agents.map((agent) => (
          <MenuItem key={agent.agent_id} value={agent.agent_id}>
            {agent.name} ({agent.specialty})
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default AgentSelector;
