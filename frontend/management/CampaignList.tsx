import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Alert, Card } from 'react-bootstrap';
import { getCampaigns, deleteCampaign } from '../shared/services/api';
import type { Campaign } from '../shared/types/api';

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
        <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
                <h3 className="mb-0">Campaigns</h3>
                <Button variant="primary" onClick={() => navigate('/campaigns/add')}>
                    Add Campaign
                </Button>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                <Table striped bordered hover>
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
                                        variant="info"
                                        size="sm"
                                        onClick={() => navigate(`/campaigns/${campaign.id}/tracking`)}
                                        className="me-2"
                                    >
                                        Tracking
                                    </Button>
                                    <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={() => navigate(`/campaigns/${campaign.id}/edit`)}
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
            </Card.Body>
        </Card>
    );
};

export default CampaignList;

