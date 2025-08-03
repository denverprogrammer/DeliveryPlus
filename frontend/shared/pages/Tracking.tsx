import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { sendTrackingData } from '../services/api';
import { getQueryParam, sendPassiveTracking } from '../services/trackingUtils';

interface TrackingResponse {
    status: string;
    message: string;
}

const Tracking = () => {
    const { token } = useParams<{ token: string }>();
    const urlToken = getQueryParam('token');
    const [inputToken, setInputToken] = useState(token || urlToken || '');
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<TrackingResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Passive enrichment request fires on page load
    useEffect(() => {
        const finalToken = inputToken || urlToken;
        if (finalToken) {
            sendPassiveTracking(finalToken, `${import.meta.env.VITE_API_URL || ''}/tracking`);
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
            const result = await sendTrackingData(inputToken);
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
                        <h5 className="mb-0">Package Tracking</h5>
                    </Card.Header>
                    <Card.Body>
                        <p className="card-text">
                            To check the status of your package, please enter your token and click the button below.
                        </p>
                        
                        <Form onSubmit={handleSubmit}>
                            <div className="d-flex align-items-center mb-3">
                                <Form.Control
                                    type="text"
                                    value={inputToken}
                                    onChange={(e) => setInputToken(e.target.value)}
                                    placeholder="Enter your tracking token"
                                    required
                                    className="me-2"
                                />
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
                                            Loading...
                                        </>
                                    ) : (
                                        'Check'
                                    )}
                                </Button>
                            </div>
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

export default Tracking; 