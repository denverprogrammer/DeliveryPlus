import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button, Form, Alert, Spinner } from 'react-bootstrap';
// import { sendTrackingData, sendRedirectData } from '../services/api';
import { sendTrackingData, sendNotifyData } from '../services/trackingUtils';

interface TrackingResponse {
    status: string;
    detail: string;
}

interface NotifyResponse {
    status: string;
    detail: string;
}

const TrackingPage = () => {
    const [queryString] = useSearchParams();
    const hasRunRef = useRef(false);


    const [inputToken, setInputToken] = useState('');
    const [isTrackingLoading, setIsTrackingLoading] = useState(false);
    const [trackingResponse, setTrackingResponse] = useState<TrackingResponse | null>(null);
    const [trackingError, setTrackingError] = useState<string | null>(null);


    const [phone, setPhone] = useState('');
    const [isNotificationLoading, setIsNotificationLoading] = useState(false);
    const [notifyResponse, setNotifyResponse] = useState<NotifyResponse | null>(null);
    const [notificationError, setNotificationError] = useState<string | null>(null);


    // Update inputToken when URL parameter changes
    useEffect(() => {
        const token: string | null = queryString.get('token');
        setInputToken(token ?? '');
    }, [queryString]);


    useEffect(() => {
        setTrackingResponse(null);
        setTrackingError(null);

        setPhone('');
        setNotifyResponse(null);
        setNotificationError(null);
    }, [inputToken]);


    // Passive enrichment request fires only on page load
    useEffect(() => {
        if (hasRunRef.current) {
            return;
        }

        hasRunRef.current = true;

        const fetchData = async () => {
            try {
                const token: string | null = queryString.get('token');

                if (token === null  || token === '' || isTrackingLoading) {
                    return;
                }

                await sendTrackingData(token, 'GET');
                
            } catch (err) { 
                // Don't catch any errors here because of passive request.
            }
        };

        fetchData();
    }, []); // Empty dependency array - only run on mount

    const handleTrackingSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputToken.trim()) {
            setTrackingError('Please enter a tracking token');
            return;
        }

        setIsTrackingLoading(true);
        setTrackingError(null);
        setTrackingResponse(null);

        try {
            const result = await sendTrackingData(inputToken, 'POST');
            setTrackingResponse(result);

            if (result.status !== 'success') {
                throw new Error(result.detail || 'Tracking request failed');
            }
        } catch (err) {
            setTrackingError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsTrackingLoading(false);
        }
    };

    const handleNotifySubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputToken.trim()) {
            setNotificationError('Please enter a tracking token');
            return;
        }

        setIsNotificationLoading(true);
        setNotificationError(null);
        setNotifyResponse(null);

        try {
            const result = await sendNotifyData(inputToken, 'POST', phone);
            setNotifyResponse(result);

            if (result.status !== 'success') {
                throw new Error(result.detail || 'Notification request failed');
            }
        } catch (err) {
            setNotificationError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsNotificationLoading(false);
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
                            disabled={isTrackingLoading}
                            className="px-4"
                        >
                            {isTrackingLoading ? (
                                <div className="d-flex align-items-center gap-3">
                                    <Spinner
                                        as="span"
                                        animation="border"
                                        size="sm"
                                        role="status"
                                        aria-hidden="true"
                                        className="me-2"
                                    />
                                    Loading...
                                </div>
                            ) : (
                                'Check'
                            )}
                        </Button>
                    </div>
                </Form>

                {trackingError && (
                    <Alert variant="danger" className="mt-3">
                        {trackingError}
                    </Alert>
                )}

                {trackingResponse && trackingResponse.status === 'success' && (
                    <div>
                        <Alert variant="success" className="mt-3">
                            {trackingResponse.detail}
                        </Alert>

                        <hr className="my-4" />

                        <Form onSubmit={handleNotifySubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label className="fw-semibold">Phone Number for Notifications (Optional)</Form.Label>
                                <div className="d-flex align-items-center gap-3">
                                    <Form.Control
                                        type="tel"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                        placeholder="Enter phone number for notifications"
                                        className="border"
                                    />
                                    <Button 
                                        type="submit" 
                                        variant="primary" 
                                        disabled={isNotificationLoading}
                                        style={{ whiteSpace: 'nowrap' }}
                                    >
                                        {isNotificationLoading ? (
                                            <div className="d-flex align-items-center gap-3">
                                                <Spinner
                                                    as="span"
                                                    animation="border"
                                                    size="sm"
                                                    role="status"
                                                    aria-hidden="true"
                                                    className="me-2"
                                                />
                                                Loading...
                                            </div>
                                        ) : (
                                            'Notify Me'
                                        )}
                                    </Button>
                                </div>
                            </Form.Group>
                        </Form>
                    </div>
                )}

                {notificationError && (
                    <Alert variant="danger" className="mt-3">
                        {notificationError}
                    </Alert>
                )}

                {notifyResponse && (
                    <Alert variant="success" className="mt-3">
                        {notifyResponse.detail}
                    </Alert>
                )}
            </div>
        </div>
    );
};

export default TrackingPage; 