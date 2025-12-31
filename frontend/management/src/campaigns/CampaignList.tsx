import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Alert } from 'react-bootstrap';
import { getCampaigns, deleteCampaign } from '../services/api';
import type { Campaign } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';

const CampaignList = () => {
    const navigate = useNavigate();
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadCampaigns = async () => {
        try {
            setIsLoading(true);
            const response = await getCampaigns();
            setCampaigns(response || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load campaigns');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadCampaigns();
    }, []);

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this campaign?')) {
            return;
        }
        try {
            await deleteCampaign(id);
            loadCampaigns();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete campaign');
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <Table striped bordered hover>
                <caption className="p-0 fw-bold" style={TABLE_CAPTION_STYLE}>
                    <div className="d-flex justify-content-between align-items-center">
                        <span>Campaigns</span>
                        <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.CAMPAIGNS}/add`)}>
                            Add Campaign
                        </Button>
                    </div>
                </caption>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Landing Page</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {campaigns.map((campaign) => (
                        <tr key={campaign.id}>
                            <td>{campaign.name}</td>
                            <td>{campaign.campaign_type}</td>
                            <td>{campaign.description || '-'}</td>
                            <td>{campaign.landing_page_url || '-'}</td>
                            <td>
                                <Button
                                    variant="primary"
                                    size="sm"
                                    onClick={() => navigate(`${ROUTES.CAMPAIGNS}/${campaign.id}`)}
                                    className="me-2"
                                >
                                    View
                                </Button>
                                <Button
                                    variant="primary"
                                    size="sm"
                                    onClick={() => navigate(`${ROUTES.CAMPAIGNS}/${campaign.id}/edit`)}
                                    className="me-2"
                                >
                                    Edit
                                </Button>
                                <Button
                                    variant="danger"
                                    size="sm"
                                    onClick={() => handleDelete(campaign.id)}
                                >
                                    Delete
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default CampaignList;

