import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Table, Alert, Button } from 'react-bootstrap';
import { getCampaign } from '../shared/services/api';
import type { Campaign } from '../shared/types/api';

const CampaignDetail = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (id) {
            loadCampaign();
        }
    }, [id]);

    const loadCampaign = async () => {
        try {
            setIsLoading(true);
            const response = await getCampaign(parseInt(id!));
            setCampaign(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load campaign');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    if (!campaign) {
        return <Alert variant="warning">Campaign not found</Alert>;
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>Campaign Details</h3>
                <div>
                    <Button
                        variant="primary"
                        size="sm"
                        onClick={() => navigate(`/campaigns/${campaign.id}/edit`)}
                        className="me-2"
                    >
                        Edit
                    </Button>
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => navigate('/campaigns')}
                    >
                        Back to List
                    </Button>
                </div>
            </div>

            <div className="row mb-4">
                <div className="col-md-6">
                    <Table striped bordered hover>
                        <tbody>
                            <tr>
                                <th style={{ width: '30%' }}>ID</th>
                                <td>{campaign.id}</td>
                            </tr>
                            <tr>
                                <th>Name</th>
                                <td>{campaign.name}</td>
                            </tr>
                            <tr>
                                <th>Type</th>
                                <td>{campaign.campaign_type}</td>
                            </tr>
                            <tr>
                                <th>Description</th>
                                <td>{campaign.description || 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Landing Page URL</th>
                                <td>
                                    {campaign.landing_page_url ? (
                                        <a href={campaign.landing_page_url} target="_blank" rel="noopener noreferrer">
                                            {campaign.landing_page_url}
                                        </a>
                                    ) : (
                                        'N/A'
                                    )}
                                </td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
                <div className="col-md-6">
                    <Table striped bordered hover>
                        <tbody>
                            <tr>
                                <th style={{ width: '30%' }}>IP Precedence</th>
                                <td>{campaign.ip_precedence || 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Location Precedence</th>
                                <td>{campaign.location_precedence || 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Locale Precedence</th>
                                <td>{campaign.locale_precedence || 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Browser Precedence</th>
                                <td>{campaign.browser_precedence || 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Time Precedence</th>
                                <td>{campaign.time_precedence || 'N/A'}</td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
            </div>

            {/* Tracking Configuration */}
            <div className="mb-4">
                <h4 className="mb-3">Tracking Configuration</h4>
                <div className="row">
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                IP Tracking
                            </caption>
                            <tbody>
                                {campaign.ip_tracking && campaign.ip_tracking.length > 0 ? (
                                    campaign.ip_tracking.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No IP tracking configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                Location Tracking
                            </caption>
                            <tbody>
                                {campaign.location_tracking && campaign.location_tracking.length > 0 ? (
                                    campaign.location_tracking.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No location tracking configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                </div>
                <div className="row mt-3">
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                Locale Tracking
                            </caption>
                            <tbody>
                                {campaign.locale_tracking && campaign.locale_tracking.length > 0 ? (
                                    campaign.locale_tracking.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No locale tracking configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                Browser Tracking
                            </caption>
                            <tbody>
                                {campaign.browser_tracking && campaign.browser_tracking.length > 0 ? (
                                    campaign.browser_tracking.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No browser tracking configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                </div>
                <div className="row mt-3">
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                Time Tracking
                            </caption>
                            <tbody>
                                {campaign.time_tracking && campaign.time_tracking.length > 0 ? (
                                    campaign.time_tracking.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No time tracking configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                    <div className="col-md-6">
                        <Table striped bordered hover size="sm">
                            <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                                Publishing Type
                            </caption>
                            <tbody>
                                {campaign.publishing_type && campaign.publishing_type.length > 0 ? (
                                    campaign.publishing_type.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td className="text-muted">No publishing types configured</td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                </div>
            </div>

            {/* Tracking Pixel */}
            {campaign.tracking_pixel && (
                <div className="mb-4">
                    <h4 className="mb-3">Tracking Pixel</h4>
                    <div className="bg-light p-3 rounded">
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {campaign.tracking_pixel}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampaignDetail;
