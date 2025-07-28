import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, Button, Alert } from 'react-bootstrap';
import { getAgents } from '../services/api';

interface Agent {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  status: string;
}

const AgentList = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await getAgents();
        setAgents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load agents');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgents();
  }, []);

  if (isLoading) {
    return <div>Loading agents...</div>;
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>Agents List</h2>
        <Link to="/agents/add" className="btn btn-primary">
          Add Agent
        </Link>
      </div>

      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {agents.length > 0 ? (
            agents.map((agent) => (
              <tr key={agent.id}>
                <td>{agent.first_name} {agent.last_name}</td>
                <td>{agent.email}</td>
                <td>{agent.status}</td>
                <td>
                  <Link 
                    to={`/agents/${agent.id}/edit`}
                    className="btn btn-outline-primary btn-sm"
                  >
                    Edit
                  </Link>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={4} className="text-center">
                No agents found.
              </td>
            </tr>
          )}
        </tbody>
      </Table>
    </div>
  );
};

export default AgentList; 