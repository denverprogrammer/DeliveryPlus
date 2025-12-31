import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import _ from 'lodash';
import { getTrackingRecord, createTracking, updateTracking, getCampaigns, getRecipients } from '../services/api';
import type { Campaign, Recipient, TrackingCreatePayload, TrackingUpdatePayload } from '../types/api';
import { useParsedParam } from '../utils/params';

interface TrackingFormData {
    campaign: string;
    recipient: string;
}

interface TrackingFormErrors {
    campaign?: string[];
    recipient?: string[];
}

const TrackingForm = () => {
    const navigate = useNavigate();
    const [trackingId] = useParsedParam('id');
    const isEdit = trackingId !== null;
    const [formData, setFormData] = useState<TrackingFormData>({
        campaign: '',
        recipient: '',
    });
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [recipients, setRecipients] = useState<Recipient[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isLoadingData, setIsLoadingData] = useState<boolean>(isEdit);
    const [error, setError] = useState<string | null>(null);
    const [errors, setErrors] = useState<TrackingFormErrors>({});

    useEffect(() => {
        loadCampaigns();
        loadRecipients();
        if (isEdit && trackingId !== null) {
            loadTracking();
        }
    }, [trackingId, isEdit]);

    const loadCampaigns = async () => {
        try {
            const response = await getCampaigns();
            setCampaigns(response || []);
        } catch (err) {
            console.error('Failed to load campaigns:', err);
        }
    };

    const loadRecipients = async () => {
        try {
            const response = await getRecipients();
            setRecipients(response || []);
        } catch (err) {
            console.error('Failed to load recipients:', err);
        }
    };

    const loadTracking = async () => {
        if (trackingId === null) {
            setError('Tracking ID is required');
            return;
        }
        try {
            setIsLoadingData(true);
            const tracking = await getTrackingRecord(trackingId);
            setFormData({
                campaign: tracking.campaign.id.toString(),
                recipient: tracking.recipient?.id.toString() || '',
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
        if (name in errors) {
            setErrors((prev) => {
                const newErrors = { ...prev };
                delete newErrors[name as keyof TrackingFormErrors];
                return newErrors;
            });
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setErrors({});

        try {
            const campaignId = parseInt(formData.campaign, 10);
            if (isNaN(campaignId)) {
                setError('Campaign is required');
                return;
            }

            if (isEdit && trackingId !== null) {
                const data: TrackingUpdatePayload = {
                    campaign: campaignId,
                    recipient: !_.isEmpty(formData.recipient) ? parseInt(formData.recipient, 10) : null,
                };
                await updateTracking(trackingId, data);
            } else {
                const data: TrackingCreatePayload = {
                    campaign: campaignId,
                    recipient: !_.isEmpty(formData.recipient) ? parseInt(formData.recipient, 10) : null,
                };
                await createTracking(data);
            }
            // Always navigate to /tracking after save
            navigate('/tracking');
        } catch (err) {
            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { data?: { errors?: TrackingFormErrors } } };
                if (axiosError.response?.data?.errors) {
                    setErrors(axiosError.response.data.errors);
                } else {
                    setError('Failed to save tracking');
                }
            } else {
                setError(err instanceof Error ? err.message : 'Failed to save tracking');
            }
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoadingData) {
        return <div>Loading...</div>;
    }

    return (
        <Card>
            <Card.Header>
                <h3 className="mb-0">{isEdit ? 'Edit Tracking' : 'Add Tracking'}</h3>
            </Card.Header>
            <Card.Body>
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                            <Form.Label>Campaign</Form.Label>
                            <Form.Select
                                name="campaign"
                                value={formData.campaign}
                                onChange={handleChange}
                                required
                                isInvalid={!!errors.campaign}
                            >
                                <option value="">Select a campaign</option>
                                {campaigns.map((campaign) => (
                                    <option key={campaign.id} value={campaign.id}>
                                        {campaign.name}
                                    </option>
                                ))}
                            </Form.Select>
                            {errors.campaign && (
                                <Form.Control.Feedback type="invalid">
                                    {errors.campaign[0]}
                                </Form.Control.Feedback>
                            )}
                        </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Recipient</Form.Label>
                        <Form.Select
                            name="recipient"
                            value={formData.recipient}
                            onChange={handleChange}
                            isInvalid={!!errors.recipient}
                        >
                            <option value="">Select a recipient</option>
                            {recipients.map((recipient) => (
                                <option key={recipient.id} value={recipient.id}>
                                    {recipient.first_name} {recipient.last_name} ({recipient.email})
                                </option>
                            ))}
                        </Form.Select>
                        {errors.recipient && (
                            <Form.Control.Feedback type="invalid">
                                {errors.recipient[0]}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    {error && (
                        <Alert variant="danger" className="mb-3">
                            {error}
                        </Alert>
                    )}

                    <div className="d-flex gap-2">
                        <Button type="submit" variant="primary" disabled={isLoading}>
                            {isLoading ? 'Saving...' : 'Save'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => navigate('/tracking')}>
                            Cancel
                        </Button>
                    </div>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default TrackingForm;

