import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { sendRedirectData } from '../services/api';
import { getQueryParam, sendPassiveTracking } from '../services/trackingUtils';

interface RedirectResponse {
    status: string;
    message: string;
}

const Redirect = () => {
    const { token } = useParams<{ token: string }>();
    const urlToken = getQueryParam('token');
    const [inputToken, setInputToken] = useState(token || urlToken || '');
    const [notifications, setNotifications] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<RedirectResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Passive enrichment request fires on page load
    useEffect(() => {
        const finalToken = inputToken || urlToken;
        if (finalToken) {
            sendPassiveTracking(finalToken, `/api/packages`);
        }
    }, [inputToken, urlToken]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputToken.trim()) {
            setError('Please enter a tracking token');
            return;
        }

        setIsLoading(true);
        setError(null);
        setResponse(null);

        try {
            const result = await sendRedirectData(inputToken, notifications || undefined);
            setResponse(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="row justify-content-center mt-4">
            <div className="col-md-8">
                <Card>
                    <Card.Header className="bg-primary text-white">
                        <h5 className="mb-0">Package Redirect</h5>
                    </Card.Header>
                    <Card.Body>
                        {/* Info box */}
                        <Alert variant="danger" className="mb-4">
                            <ul className="mb-0">
                                <li>Please enable GPS if asked. GPS allows the site to show closer delivery locations or faster routes. International locations are also available.</li>
                                <li>Notifications are required to receive new package updates. The original sender will not receive new updates.</li>
                                <li>For your privacy the original sender will not be notified of the redirect. The recipient will be responsible for any additional delivery charges incurred.</li>
                            </ul>
                        </Alert>

                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Tracking Token</Form.Label>
                                <Form.Control
                                    type="text"
                                    value={inputToken}
                                    onChange={(e) => setInputToken(e.target.value)}
                                    placeholder="Enter your tracking token"
                                    required
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Phone Number for Notifications (Optional)</Form.Label>
                                <Form.Control
                                    type="tel"
                                    value={notifications}
                                    onChange={(e) => setNotifications(e.target.value)}
                                    placeholder="Enter phone number for notifications"
                                />
                                <Form.Text className="text-muted">
                                    You'll receive SMS updates about your package redirect
                                </Form.Text>
                            </Form.Group>

                            <Button 
                                type="submit" 
                                variant="primary" 
                                disabled={isLoading}
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
                                    'Redirect Package'
                                )}
                            </Button>
                        </Form>

                        {error && (
                            <Alert variant="danger" className="mt-3">
                                {error}
                            </Alert>
                        )}

                        {response && (
                            <Alert variant="success" className="mt-3">
                                {response.message}
                            </Alert>
                        )}
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
};

export default Redirect; 