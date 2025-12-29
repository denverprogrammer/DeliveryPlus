import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Table, Button, Alert, Card } from 'react-bootstrap';
import { getTrackingRecord } from '../shared/services/api';
import type { Tracking, Token, RequestData } from '../shared/types/api';
import RequestDataModal from './RequestDataModal';

const TrackingDetail = () => {
    const navigate = useNavigate();
    const { campaignId, id } = useParams<{ campaignId: string; id: string }>();
    const [tracking, setTracking] = useState<Tracking | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [selectedRequestDataId, setSelectedRequestDataId] = useState<number | null>(null);

    useEffect(() => {
        if (id) {
            loadTracking();
        }
    }, [id]);

    const loadTracking = async () => {
        try {
            setIsLoading(true);
            const response = await getTrackingRecord(parseInt(id!));
            setTracking(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch {
            return dateString;
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    if (!tracking) {
        return <Alert variant="warning">Tracking record not found</Alert>;
    }

    const tokens = tracking.tokens || [];
    const requestData = tracking.request_data || [];

    return (
        <div>
            <Card className="mb-4">
                <Card.Header className="d-flex justify-content-between align-items-center">
                    <h3 className="mb-0">Tracking Details</h3>
                    <Button variant="secondary" onClick={() => navigate(`/campaigns/${campaignId}/tracking`)}>
                        Back to List
                    </Button>
                </Card.Header>
                <Card.Body>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p><strong>Campaign:</strong> {tracking.campaign_name}</p>
                            <p><strong>Recipient:</strong> {tracking.recipient_name || 'N/A'}</p>
                        </div>
                        <div className="col-md-6">
                            <p><strong>Request Count:</strong> {tracking.count_requests || 0}</p>
                        </div>
                    </div>
                </Card.Body>
            </Card>

            {/* Tokens Section */}
            <Card className="mb-4">
                <Card.Header>
                    <h4 className="mb-0">Tokens</h4>
                </Card.Header>
                <Card.Body>
                    {tokens.length > 0 ? (
                        <Table striped bordered hover>
                            <thead>
                                <tr>
                                    <th>Value</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Last Used</th>
                                    <th>Used</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tokens.map((token: Token) => (
                                    <tr key={token.id}>
                                        <td>{token.value}</td>
                                        <td>{token.status}</td>
                                        <td>{formatDate(token.created_on)}</td>
                                        <td>{token.last_used ? formatDate(token.last_used) : 'N/A'}</td>
                                        <td>{token.used !== undefined ? token.used : tracking.count_requests || 0}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    ) : (
                        <p className="text-muted">No tokens found.</p>
                    )}
                </Card.Body>
            </Card>

            {/* Request Data Section */}
            <Card>
                <Card.Header>
                    <h4 className="mb-0">Request Data</h4>
                </Card.Header>
                <Card.Body>
                    {requestData.length > 0 ? (
                        <div className="table-responsive">
                            <Table striped bordered hover size="sm">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Timestamp</th>
                                        <th>Type</th>
                                        <th>Method</th>
                                        <th>IP Address</th>
                                        <th>OS</th>
                                        <th>Browser</th>
                                        <th>Platform</th>
                                        <th>Locale</th>
                                        <th>Client Time</th>
                                        <th>Location</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {requestData.map((req: RequestData) => (
                                        <tr key={req.id}>
                                            <td>{req.id}</td>
                                            <td>
                                                <button
                                                    className="btn btn-link p-0"
                                                    style={{ textDecoration: 'underline', border: 'none', background: 'none', color: '#0d6efd' }}
                                                    onClick={() => {
                                                        setSelectedRequestDataId(req.id);
                                                        setShowModal(true);
                                                    }}
                                                >
                                                    {formatDate(req.server_timestamp)}
                                                </button>
                                            </td>
                                            <td>{req.data_type || 'N/A'}</td>
                                            <td>{req.http_method || 'N/A'}</td>
                                            <td>{req.ip_address || 'N/A'}</td>
                                            <td>{req.os || 'N/A'}</td>
                                            <td>{req.browser || 'N/A'}</td>
                                            <td>{req.platform || 'N/A'}</td>
                                            <td>{req.locale || 'N/A'}</td>
                                            <td>{req.client_time ? formatDate(req.client_time) : 'N/A'}</td>
                                            <td>
                                                {req.latitude && req.longitude 
                                                    ? `${req.latitude.toFixed(4)}, ${req.longitude.toFixed(4)}`
                                                    : 'N/A'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        </div>
                    ) : (
                        <p className="text-muted">No request data found.</p>
                    )}
                </Card.Body>
            </Card>

            <RequestDataModal
                show={showModal}
                onHide={() => {
                    setShowModal(false);
                    setSelectedRequestDataId(null);
                }}
                requestDataId={selectedRequestDataId}
            />
        </div>
    );
};

export default TrackingDetail;

