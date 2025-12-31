import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getCampaign, createCampaign, updateCampaign } from '../services/api';
import { useParsedParam } from '../utils/params';
import type { CampaignCreatePayload, CampaignUpdatePayload } from '../types/api';

interface CampaignFormData {
    name: string;
    description: string;
    campaign_type: string;
    publishing_type: string[];
    landing_page_url: string;
    tracking_pixel: string;
    ip_precedence: string;
    location_precedence: string;
    locale_precedence: string;
    browser_precedence: string;
    time_precedence: string;
    ip_tracking: string[];
    location_tracking: string[];
    locale_tracking: string[];
    browser_tracking: string[];
    time_tracking: string[];
}

const CAMPAIGN_TYPES = [
    { value: 'packages', label: 'Packages' },
    { value: 'images', label: 'Images' },
    { value: 'invites', label: 'Invites' },
    { value: 'directions', label: 'Directions' },
    { value: 'speedtest', label: 'Speedtest' },
    { value: 'addsense', label: 'Addsense' },
    { value: 'chat', label: 'Chat' },
    { value: 'vpn', label: 'VPN' },
];

const TRACKING_TYPES = [
    { value: 'server', label: 'Server' },
    { value: 'client', label: 'Client' },
];

const PUBLISHING_TYPES = [
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
];

const CampaignForm = () => {
    const navigate = useNavigate();
    const [campaignId] = useParsedParam('id');
    const isEdit = campaignId !== null;
    const [formData, setFormData] = useState<CampaignFormData>({
        name: '',
        description: '',
        campaign_type: 'packages',
        publishing_type: [],
        landing_page_url: '',
        tracking_pixel: '',
        ip_precedence: 'server',
        location_precedence: 'server',
        locale_precedence: 'server',
        browser_precedence: 'server',
        time_precedence: 'server',
        ip_tracking: [],
        location_tracking: [],
        locale_tracking: [],
        browser_tracking: [],
        time_tracking: [],
    });
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingData, setIsLoadingData] = useState(isEdit);
    const [error, setError] = useState<string | null>(null);
    const [errors, setErrors] = useState<Record<string, string[]>>({});

    useEffect(() => {
        if (isEdit && campaignId !== null) {
            loadCampaign();
        }
    }, [campaignId, isEdit]);

    const loadCampaign = async () => {
        if (campaignId === null) {
            return;
        }
        try {
            setIsLoadingData(true);
            const campaign = await getCampaign(campaignId);
            setFormData({
                name: campaign.name || '',
                description: campaign.description || '',
                campaign_type: campaign.campaign_type || 'packages',
                publishing_type: campaign.publishing_type || [],
                landing_page_url: campaign.landing_page_url || '',
                tracking_pixel: campaign.tracking_pixel || '',
                ip_precedence: campaign.ip_precedence || 'server',
                location_precedence: campaign.location_precedence || 'server',
                locale_precedence: campaign.locale_precedence || 'server',
                browser_precedence: campaign.browser_precedence || 'server',
                time_precedence: campaign.time_precedence || 'server',
                ip_tracking: campaign.ip_tracking || [],
                location_tracking: campaign.location_tracking || [],
                locale_tracking: campaign.locale_tracking || [],
                browser_tracking: campaign.browser_tracking || [],
                time_tracking: campaign.time_tracking || [],
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load campaign');
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const value = e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: value,
        });
        if (errors[e.target.name]) {
            const newErrors = { ...errors };
            delete newErrors[e.target.name];
            setErrors(newErrors);
        }
    };

    const handleCheckboxChange = (name: string, value: string, checked: boolean) => {
        const currentArray = formData[name as keyof typeof formData] as string[];
        const newArray = checked
            ? [...currentArray, value]
            : currentArray.filter((item) => item !== value);
        setFormData({
            ...formData,
            [name]: newArray,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setErrors({});

        try {
            if (isEdit && campaignId !== null) {
                const data: CampaignUpdatePayload = {
                    name: formData.name,
                    description: formData.description,
                    campaign_type: formData.campaign_type,
                    publishing_type: formData.publishing_type,
                    landing_page_url: formData.landing_page_url,
                    tracking_pixel: formData.tracking_pixel,
                    ip_precedence: formData.ip_precedence,
                    location_precedence: formData.location_precedence,
                    locale_precedence: formData.locale_precedence,
                    browser_precedence: formData.browser_precedence,
                    time_precedence: formData.time_precedence,
                    ip_tracking: formData.ip_tracking,
                    location_tracking: formData.location_tracking,
                    locale_tracking: formData.locale_tracking,
                    browser_tracking: formData.browser_tracking,
                    time_tracking: formData.time_tracking,
                };
                await updateCampaign(campaignId, data);
            } else {
                const data: CampaignCreatePayload = {
                    name: formData.name,
                    description: formData.description,
                    campaign_type: formData.campaign_type,
                    publishing_type: formData.publishing_type,
                    landing_page_url: formData.landing_page_url,
                    tracking_pixel: formData.tracking_pixel,
                    ip_precedence: formData.ip_precedence,
                    location_precedence: formData.location_precedence,
                    locale_precedence: formData.locale_precedence,
                    browser_precedence: formData.browser_precedence,
                    time_precedence: formData.time_precedence,
                    ip_tracking: formData.ip_tracking,
                    location_tracking: formData.location_tracking,
                    locale_tracking: formData.locale_tracking,
                    browser_tracking: formData.browser_tracking,
                    time_tracking: formData.time_tracking,
                };
                await createCampaign(data);
            }
            navigate('/campaigns');
        } catch (err) {
            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { data?: { errors?: Record<string, string[]> } } };
                if (axiosError.response?.data?.errors) {
                    const errors = axiosError.response.data.errors;
                    setErrors(errors);
                    // Also set a general error message
                    const errorMessages: string[] = [];
                    Object.entries(errors).forEach(([field, messages]) => {
                        if (Array.isArray(messages)) {
                            messages.forEach((msg: string) => {
                                errorMessages.push(`${field}: ${msg}`);
                            });
                        } else {
                            errorMessages.push(`${field}: ${String(messages)}`);
                        }
                    });
                    setError(errorMessages.join(', '));
                } else {
                    setError('Failed to save campaign');
                }
            } else {
                setError(err instanceof Error ? err.message : 'Failed to save campaign');
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
                <h3 className="mb-0">{isEdit ? 'Edit Campaign' : 'Add Campaign'}</h3>
            </Card.Header>
            <Card.Body>
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            isInvalid={!!errors.name}
                        />
                        {errors.name && (
                            <Form.Control.Feedback type="invalid">
                                {errors.name[0]}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Description</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Campaign Type</Form.Label>
                        <Form.Select
                            name="campaign_type"
                            value={formData.campaign_type}
                            onChange={handleChange}
                            required
                        >
                            {CAMPAIGN_TYPES.map((type) => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </Form.Select>
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Publishing Type</Form.Label>
                        {PUBLISHING_TYPES.map((type) => (
                            <Form.Check
                                key={type.value}
                                type="checkbox"
                                label={type.label}
                                checked={formData.publishing_type.includes(type.value)}
                                onChange={(e) => handleCheckboxChange('publishing_type', type.value, e.target.checked)}
                            />
                        ))}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Landing Page URL</Form.Label>
                        <Form.Control
                            type="url"
                            name="landing_page_url"
                            value={formData.landing_page_url}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Tracking Pixel</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            name="tracking_pixel"
                            value={formData.tracking_pixel}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    <h5>Precedence Settings</h5>
                    {['ip', 'location', 'locale', 'browser', 'time'].map((type) => (
                        <Form.Group key={type} className="mb-3">
                            <Form.Label>{type.charAt(0).toUpperCase() + type.slice(1)} Precedence</Form.Label>
                            <Form.Select
                                name={`${type}_precedence`}
                                value={formData[`${type}_precedence` as keyof typeof formData] as string}
                                onChange={handleChange}
                            >
                                {TRACKING_TYPES.map((t) => (
                                    <option key={t.value} value={t.value}>
                                        {t.label}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                    ))}

                    <h5>Tracking Settings</h5>
                    {['ip', 'location', 'locale', 'browser', 'time'].map((type) => (
                        <Form.Group key={type} className="mb-3">
                            <Form.Label>{type.charAt(0).toUpperCase() + type.slice(1)} Tracking</Form.Label>
                            {TRACKING_TYPES.map((t) => (
                                <Form.Check
                                    key={t.value}
                                    type="checkbox"
                                    label={t.label}
                                    checked={(formData[`${type}_tracking` as keyof typeof formData] as string[]).includes(t.value)}
                                    onChange={(e) => handleCheckboxChange(`${type}_tracking`, t.value, e.target.checked)}
                                />
                            ))}
                        </Form.Group>
                    ))}

                    {error && (
                        <Alert variant="danger" className="mb-3">
                            {error}
                        </Alert>
                    )}

                    <div className="d-flex gap-2">
                        <Button type="submit" variant="primary" disabled={isLoading}>
                            {isLoading ? 'Saving...' : 'Save'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => navigate('/campaigns')}>
                            Cancel
                        </Button>
                    </div>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default CampaignForm;

