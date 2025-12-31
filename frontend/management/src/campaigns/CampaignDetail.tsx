import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Alert, Button } from 'react-bootstrap';
import { getCampaign } from '../services/api';
import type { Campaign } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import { isNonEmptyArray } from '../utils/typeGuards';
import { useParsedParam } from '../utils/params';

const CampaignDetail = () => {
    const navigate = useNavigate();
    const [campaignId] = useParsedParam('id');
    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (campaignId !== null) {
            loadCampaign();
        } else {
            setError('Invalid campaign ID');
            setIsLoading(false);
        }
    }, [campaignId]);

    const loadCampaign = async () => {
        if (campaignId === null) {
            return;
        }
        try {
            setIsLoading(true);
            const response = await getCampaign(campaignId);
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
                        onClick={() => navigate(`${ROUTES.CAMPAIGNS}/${campaign.id}/edit`)}
                        className="me-2"
                    >
                        Edit
                    </Button>
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => navigate(ROUTES.CAMPAIGNS)}
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
                                <th className="w-25">ID</th>
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
                                <th className="w-25">IP Precedence</th>
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                IP Tracking
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.ip_tracking) ? (
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                Location Tracking
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.location_tracking) ? (
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                Locale Tracking
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.locale_tracking) ? (
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                Browser Tracking
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.browser_tracking) ? (
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                Time Tracking
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.time_tracking) ? (
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
                            <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                                Publishing Type
                            </caption>
                            <tbody>
                                {isNonEmptyArray(campaign.publishing_type) ? (
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
                        <pre className="m-0" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {campaign.tracking_pixel}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampaignDetail;
