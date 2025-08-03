import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getAgent, createAgent, updateAgent } from '../shared/services/api';

interface AgentFormData {
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    status: string;
}

const AgentForm = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const isEditing = Boolean(id);

    const [formData, setFormData] = useState<AgentFormData>({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        status: 'active',
    });

    const [isLoading, setIsLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(isEditing);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isEditing && id) {
            const fetchAgent = async () => {
                try {
                    const agent = await getAgent(parseInt(id));
                    setFormData({
                        first_name: agent.first_name || '',
                        last_name: agent.last_name || '',
                        email: agent.email || '',
                        phone_number: agent.phone_number || '',
                        status: agent.status || 'active',
                    });
                } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to load agent');
                } finally {
                    setIsInitialLoading(false);
                }
            };

            fetchAgent();
        } else {
            setIsInitialLoading(false);
        }
    }, [id, isEditing]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            if (isEditing && id) {
                await updateAgent(parseInt(id), formData);
            } else {
                await createAgent(formData);
            }
            navigate('/mgmt/agents');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save agent');
        } finally {
            setIsLoading(false);
        }
    };

    if (isInitialLoading) {
        return <div>Loading agent...</div>;
    }

    return (
        <div className="row justify-content-center">
            <div className="col-md-8">
                <Card>
                    <Card.Header>
                        <h2 className="mb-0">{isEditing ? 'Edit Agent' : 'Add Agent'}</h2>
                    </Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>First Name</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Last Name</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Email</Form.Label>
                                <Form.Control
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Phone Number</Form.Label>
                                <Form.Control
                                    type="tel"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Status</Form.Label>
                                <Form.Select
                                    name="status"
                                    value={formData.status}
                                    onChange={handleChange}
                                >
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </Form.Select>
                            </Form.Group>

                            {error && (
                                <Alert variant="danger" className="mb-3">
                                    {error}
                                </Alert>
                            )}

                            <div className="d-flex gap-2">
                                <Button 
                                    type="submit" 
                                    variant="primary" 
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Saving...' : (isEditing ? 'Update' : 'Create')}
                                </Button>
                                <Button 
                                    type="button" 
                                    variant="secondary" 
                                    onClick={() => navigate('/mgmt/agents')}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </Form>
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
};

export default AgentForm; 