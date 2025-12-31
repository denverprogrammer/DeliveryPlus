import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Alert } from 'react-bootstrap';
import { getTracking, deleteTracking } from '../services/api';
import type { TrackingListItem } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import { isNonEmptyArray } from '../utils/typeGuards';

const TrackingList = () => {
    const navigate = useNavigate();
    const [tracking, setTracking] = useState<TrackingListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadTracking = async () => {
        try {
            setIsLoading(true);
            const response = await getTracking();
            setTracking(response || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadTracking();
    }, []);

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

    const handleView = (record: TrackingListItem) => {
        // Navigate to the top-level tracking detail page
        navigate(`${ROUTES.TRACKING}/${record.id}`);
    };

    const handleEdit = (record: TrackingListItem) => {
        // Navigate to the top-level tracking edit page
        navigate(`${ROUTES.TRACKING}/${record.id}/edit`);
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
                        <span>Tracking</span>
                        <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.TRACKING}/add`)}>
                            Add Tracking
                        </Button>
                    </div>
                </caption>
                <thead>
                    <tr>
                        <th>Campaign</th>
                        <th>Recipient</th>
                        <th>Request Count</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {isNonEmptyArray(tracking) ? (
                        tracking.map((record) => (
                            <tr key={record.id}>
                                <td>{record.campaign?.name || 'N/A'}</td>
                                <td>{record.recipient?.full_name || 'N/A'}</td>
                                <td>{record.count_requests || 0}</td>
                                <td>
                                    <Button
                                        variant="info"
                                        size="sm"
                                        onClick={() => handleView(record)}
                                        className="me-2"
                                    >
                                        View
                                    </Button>
                                    <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={() => handleEdit(record)}
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
                            <td colSpan={4} className="text-center">
                                No tracking records found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </Table>
        </div>
    );
};

export default TrackingList;

