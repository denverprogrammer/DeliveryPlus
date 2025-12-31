import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Alert, Card } from 'react-bootstrap';
import _ from 'lodash';
import { getTracking, deleteTracking, getCampaign } from '../shared/services/api';
import type { Tracking } from '../shared/types/api';
import { isCampaignObject, isNonEmptyArray } from './utils/typeGuards';
import { useParsedParam } from './utils/params';

const TrackingList = () => {
    const navigate = useNavigate();
    const [campaignId] = useParsedParam('campaignId');
    const [tracking, setTracking] = useState<Tracking[]>([]);
    const [campaignName, setCampaignName] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const loadCampaign = async () => {
        if (campaignId === null) {
            return;
        }
        try {
            const campaign = await getCampaign(campaignId);
            setCampaignName(campaign.name);
        } catch (err) {
            console.error('Failed to load campaign:', err);
            setError(err instanceof Error ? err.message : 'Failed to load campaign');
        }
    };

    const loadTracking = async () => {
        try {
            setIsLoading(true);
            const response = await getTracking();
            // Filter by campaign if campaignId is provided
            if (campaignId !== null) {
                const filtered = response.filter((t: Tracking) => {
                    const trackingCampaignId = isCampaignObject(t.campaign)
                        ? t.campaign.id
                        : _.isNumber(t.campaign) ? t.campaign : null;
                    return trackingCampaignId === campaignId;
                });
                setTracking(filtered);
            } else {
                setTracking(response || []);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (campaignId !== null) {
            loadCampaign();
        }
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
                {campaignId !== null && (
                    <Button variant="primary" onClick={() => navigate(`/campaigns/${campaignId}/tracking/add`)}>
                        Add Tracking
                    </Button>
                )}
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
                        {isNonEmptyArray(tracking) ? (
                            tracking.map((record) => (
                                <tr key={record.id}>
                                    <td>{record.recipient_name || 'N/A'}</td>
                                    <td>{record.count_requests || 0}</td>
                                    <td>
                                        {campaignId !== null && (
                                            <>
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
                                            </>
                                        )}
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

