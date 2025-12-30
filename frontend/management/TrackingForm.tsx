import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getTrackingRecord, createTracking, updateTracking } from '../shared/services/api';
import { getCampaigns, getRecipients } from '../shared/services/api';

interface Campaign {
    id: number;
    name: string;
}

interface Recipient {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
}

const TrackingForm = () => {
    const navigate = useNavigate();
    const { campaignId, id } = useParams<{ campaignId: string; id: string }>();
    const isEdit = !!id;
    const [formData, setFormData] = useState({
        campaign: campaignId || '',
        recipient: '',
    });
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [recipients, setRecipients] = useState<Recipient[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingData, setIsLoadingData] = useState(isEdit);
    const [error, setError] = useState<string | null>(null);
    const [errors, setErrors] = useState<Record<string, string[]>>({});

    useEffect(() => {
        if (campaignId) {
            setFormData(prev => ({ ...prev, campaign: campaignId }));
        } else {
            // Only load campaigns if not nested under a campaign
            loadCampaigns();
        }
        loadRecipients();
        if (isEdit && id) {
            loadTracking();
        }
    }, [id, isEdit, campaignId]);

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
        try {
            setIsLoadingData(true);
            const response = await getTrackingRecord(parseInt(id!));
            const tracking = response;
            // Handle both object and ID formats
            const campaignId = typeof tracking.campaign === 'object' 
                ? tracking.campaign?.id 
                : tracking.campaign;
            const recipientId = typeof tracking.recipient === 'object'
                ? tracking.recipient?.id
                : tracking.recipient;
            setFormData({
                campaign: campaignId?.toString() || '',
                recipient: recipientId?.toString() || '',
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        if (errors[e.target.name]) {
            const newErrors = { ...errors };
            delete newErrors[e.target.name];
            setErrors(newErrors);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setErrors({});

        try {
            const data: any = {
                campaign: parseInt(formData.campaign),
            };
            // Only include recipient if it's not empty
            if (formData.recipient && formData.recipient !== '') {
                data.recipient = parseInt(formData.recipient);
            } else {
                data.recipient = null;
            }

            if (isEdit && id) {
                await updateTracking(parseInt(id), data);
            } else {
                await createTracking(data);
            }
            // Always navigate to /tracking after save
            navigate('/tracking');
        } catch (err: any) {
            if (err.response?.data?.errors) {
                setErrors(err.response.data.errors);
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
                    {!campaignId && (
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
                    )}

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

