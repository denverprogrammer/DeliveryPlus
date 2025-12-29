import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Table, Button, Alert, Card } from 'react-bootstrap';
import { getTracking, deleteTracking, getCampaign } from '../shared/services/api';
import type { Tracking } from '../shared/types/api';

const TrackingList = () => {
    const navigate = useNavigate();
    const { campaignId } = useParams<{ campaignId: string }>();
    const [tracking, setTracking] = useState<Tracking[]>([]);
    const [campaignName, setCampaignName] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadCampaign = async () => {
        if (!campaignId) return;
        try {
            const campaign = await getCampaign(parseInt(campaignId));
            setCampaignName(campaign.name);
        } catch (err) {
            console.error('Failed to load campaign:', err);
        }
    };

    const loadTracking = async () => {
        try {
            setIsLoading(true);
            const response = await getTracking();
            // Filter by campaign if campaignId is provided
            const filtered = campaignId 
                ? response.filter((t: Tracking) => {
                    const campaignIdNum = typeof t.campaign === 'object' ? t.campaign?.id : t.campaign;
                    return campaignIdNum === parseInt(campaignId);
                })
                : response;
            setTracking(filtered || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadCampaign();
        loadTracking();
    }, [campaignId]);

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this tracking record?')) {
            return;
        }
        try {
            await deleteTracking(id);
            loadTracking();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete tracking');
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
                <div>
                    <h3 className="mb-0">Tracking</h3>
                    {campaignName && <small className="text-muted">Campaign: {campaignName}</small>}
                </div>
                <Button variant="primary" onClick={() => navigate(`/campaigns/${campaignId}/tracking/add`)}>
                    Add Tracking
                </Button>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Recipient</th>
                            <th>Request Count</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tracking.length > 0 ? (
                            tracking.map((record) => (
                                <tr key={record.id}>
                                    <td>{record.recipient_name || 'N/A'}</td>
                                    <td>{record.count_requests || 0}</td>
                                    <td>
                                        <Button
                                            variant="info"
                                            size="sm"
                                            onClick={() => navigate(`/campaigns/${campaignId}/tracking/${record.id}`)}
                                            className="me-2"
                                        >
                                            View
                                        </Button>
                                        <Button
                                            variant="primary"
                                            size="sm"
                                            onClick={() => navigate(`/campaigns/${campaignId}/tracking/${record.id}/edit`)}
                                            className="me-2"
                                        >
                                            Edit
                                        </Button>
                                        <Button
                                            variant="danger"
                                            size="sm"
                                            onClick={() => handleDelete(record.id)}
                                        >
                                            Delete
                                        </Button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={3} className="text-center">
                                    No tracking records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </Table>
            </Card.Body>
        </Card>
    );
};

export default TrackingList;

