import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getCompanyAPI, updateCompanyAPI } from '../shared/services/api';
import type { CompanyUpdatePayload } from '../shared/types/api';

interface CompanyFormData {
    name: string;
    street_address: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
    phone_number: string;
}

const CompanyEdit = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState<CompanyFormData>({
        name: '',
        street_address: '',
        city: '',
        state: '',
        zip_code: '',
        country: '',
        phone_number: '',
    });

    const [isLoading, setIsLoading] = useState(false);
    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCompany = async () => {
            try {
                const response = await getCompanyAPI();
                const company = response;
                setFormData({
                    name: company.name || '',
                    street_address: company.street_address || '',
                    city: company.city || '',
                    state: company.state || '',
                    zip_code: company.zip_code || '',
                    country: company.country || '',
                    phone_number: company.phone_number || '',
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
            const data: CompanyUpdatePayload = {
                name: formData.name,
                street_address: formData.street_address,
                city: formData.city,
                state: formData.state,
                zip_code: formData.zip_code,
                country: formData.country,
                phone_number: formData.phone_number,
            };
            await updateCompanyAPI(data);
            navigate('/dashboard');
        } catch (err: any) {
            // Handle error response
            if (err.response?.data?.errors) {
                const errors = err.response.data.errors;
                // Format error messages
                const errorMessages: string[] = [];
                Object.entries(errors).forEach(([field, messages]) => {
                    if (Array.isArray(messages)) {
                        messages.forEach((msg: string) => {
                            errorMessages.push(`${field}: ${msg}`);
                        });
                    } else {
                        errorMessages.push(`${field}: ${messages}`);
                    }
                });
                setError(errorMessages.join(', '));
            } else {
                setError(err instanceof Error ? err.message : 'Failed to save company');
            }
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

                            <Form.Group className="mb-3">
                                <Form.Label>Street Address</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="street_address"
                                    value={formData.street_address}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>City</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>State</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="state"
                                    value={formData.state}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Zip Code</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="zip_code"
                                    value={formData.zip_code}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Country</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Phone Number</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                />
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
                                    {isLoading ? 'Saving...' : 'Update Company'}
                                </Button>
                                <Button 
                                    type="button" 
                                    variant="secondary" 
                                    onClick={() => navigate('/dashboard')}
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