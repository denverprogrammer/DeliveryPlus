import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getCompany, updateCompany } from '../shared/services/api';

interface CompanyFormData {
    name: string;
    // Add other company fields as needed
}

const CompanyEdit = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState<CompanyFormData>({
        name: '',
    });

    const [isLoading, setIsLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCompany = async () => {
            try {
                const company = await getCompany();
                setFormData({
                    name: company.name || '',
                    // Add other fields as needed
                });
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load company');
            } finally {
                setIsInitialLoading(false);
            }
        };

        fetchCompany();
    }, []);

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
            await updateCompany(formData);
            navigate('/mgmt/dashboard');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save company');
        } finally {
            setIsLoading(false);
        }
    };

    if (isInitialLoading) {
        return <div>Loading company...</div>;
    }

    return (
        <div className="row justify-content-center">
            <div className="col-md-8">
                <Card>
                    <Card.Header>
                        <h2 className="mb-0">Edit Company</h2>
                    </Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Company Name</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>

                            {/* Add more company fields as needed */}

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
                                    {isLoading ? 'Saving...' : 'Update Company'}
                                </Button>
                                <Button 
                                    type="button" 
                                    variant="secondary" 
                                    onClick={() => navigate('/mgmt/dashboard')}
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

export default CompanyEdit; 