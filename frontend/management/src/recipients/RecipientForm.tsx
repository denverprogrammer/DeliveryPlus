import React, { useState, useEffect } from 'react';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getRecipient, createRecipient, updateRecipient } from '../services/api';
import { useParsedParam } from '../utils/params';
import { useNavigator } from '../utils/routes';

interface RecipientFormData {
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    status: string;
}

const RecipientForm = () => {
    const [recipientId] = useParsedParam('id');
    const navigator = useNavigator();
    const isEditing = recipientId !== null;

    const [formData, setFormData] = useState<RecipientFormData>({
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
        if (isEditing && recipientId !== null) {
            const fetchRecipient = async () => {
                try {
                    const recipient = await getRecipient(recipientId);
                    setFormData({
                        first_name: recipient.first_name || '',
                        last_name: recipient.last_name || '',
                        email: recipient.email || '',
                        phone_number: recipient.phone_number || '',
                        status: recipient.status || 'active',
                    });
                } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to load recipient');
                } finally {
                    setIsInitialLoading(false);
                }
            };

            fetchRecipient();
        } else {
            setIsInitialLoading(false);
        }
    }, [recipientId, isEditing]);

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
            if (isEditing && recipientId !== null) {
                await updateRecipient(recipientId, formData);
            } else {
                await createRecipient(formData);
            }
            navigator.sendToRecipients();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save recipient');
        } finally {
            setIsLoading(false);
        }
    };

    if (isInitialLoading) {
        return <div>Loading recipient...</div>;
    }

    return (
        <div className="row justify-content-center">
            <div className="col-md-8">
                <Card>
                    <Card.Header>
                        <h2 className="mb-0">{isEditing ? 'Edit Recipient' : 'Add Recipient'}</h2>
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
                                    onClick={() => navigator.sendToRecipients()}
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

export default RecipientForm;

