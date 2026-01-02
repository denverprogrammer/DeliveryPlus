import { useEffect, useState, useCallback } from 'react';
import { Alert } from 'react-bootstrap';
import { GridApi } from 'ag-grid-community';
import { getTrackingRecord, getRequestDataList, getTokenList, disableToken, reactivateToken, createToken } from '../services/api';
import type { TrackingDetail, Token, RequestData } from '../types/api';
import RequestDataModal from '../RequestDataModal';
import { TABLE_CAPTION_STYLE, NOT_AVAILABLE } from '../constants/ui';
import { useParsedParam } from '../utils/params';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import { useColumnDefs } from '../hooks/useColumnDefs';

const TrackingDetail = () => {
    const [trackingId] = useParsedParam('id');
    const [tracking, setTracking] = useState<TrackingDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [selectedRequestDataId, setSelectedRequestDataId] = useState<number | null>(null);
    
    // Request data state
    const [requestData, setRequestData] = useState<RequestData[]>([]);
    const [requestDataLoading, setRequestDataLoading] = useState(false);
    const [requestDataError, setRequestDataError] = useState<string | null>(null);
    const [rowCount, setRowCount] = useState(0);
    
    // Token state
    const [tokens, setTokens] = useState<Token[]>([]);
    const [tokensLoading, setTokensLoading] = useState(false);
    const [tokensError, setTokensError] = useState<string | null>(null);

    useEffect(() => {
        if (trackingId !== null) {
            loadTracking();
        } else {
            setError('Invalid tracking ID');
            setIsLoading(false);
        }
    }, [trackingId]);

    const loadTracking = async () => {
        if (trackingId === null) {
            return;
        }
        try {
            setIsLoading(true);
            const tracking = await getTrackingRecord(trackingId);
            setTracking(tracking);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    const loadRequestData = useCallback(async (pagination: PaginationParams, _api: GridApi<RequestData>): Promise<void> => {
        if (trackingId === null) {
            return;
        }

        try {
            setRequestDataLoading(true);
            setRequestDataError(null);

            const response = await getRequestDataList({
                tracking_id: trackingId,
                ...(pagination.filters || {}),
                ...pagination,
            });
            
            setRequestData(response.results);
            setRowCount(response.count);
        } catch (err) {
            setRequestDataError(err instanceof Error ? err.message : 'Failed to load request data');
            setRequestData([]);
            setRowCount(0);
        } finally {
            setRequestDataLoading(false);
        }
    }, [trackingId]);

    const handleViewRequestData = useCallback((requestData: RequestData) => {
        setSelectedRequestDataId(requestData.id);
        setShowModal(true);
    }, []);

    const handleDisableToken = useCallback(async (token: Token) => {
        if (!window.confirm('Are you sure you want to disable this token?')) {
            return;
        }
        try {
            await disableToken(token.id);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to disable token');
        }
    }, [loadTracking]);

    const handleReactivateToken = useCallback(async (token: Token) => {
        try {
            await reactivateToken(token.id);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to reactivate token');
        }
    }, [loadTracking]);

    const handleCreateToken = async () => {
        if (trackingId === null) return;
        try {
            await createToken(trackingId);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create token');
        }
    };

    const requestDataColumnDefs = useColumnDefs<RequestData>('requestData', { view: handleViewRequestData });

    const loadTokens = useCallback(async (pagination: PaginationParams, _api: GridApi<Token>): Promise<void> => {
        if (trackingId === null) {
            return;
        }

        try {
            setTokensLoading(true);
            setTokensError(null);

            const response = await getTokenList({
                tracking_id: trackingId,
                ...pagination,
            });
            
            setTokens(response.results);
        } catch (err) {
            setTokensError(err instanceof Error ? err.message : 'Failed to load tokens');
            setTokens([]);
        } finally {
            setTokensLoading(false);
        }
    }, [trackingId]);

    const tokenColumnDefs = useColumnDefs<Token>('token', { disable: handleDisableToken, reactivate: handleReactivateToken });


    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    if (!tracking) {
        return <Alert variant="warning">Tracking record not found</Alert>;
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3 className="mb-0">Tracking Details</h3>
            </div>
            <div className="row mb-4">
                <div className="col-md-6">
                    <p><strong>Campaign:</strong> {tracking.campaign?.name || NOT_AVAILABLE}</p>
                    <p><strong>Recipient:</strong> {tracking.recipient?.full_name || NOT_AVAILABLE}</p>
                </div>
                <div className="col-md-6">
                    <p><strong>Request Count:</strong> {tracking.count_requests || 0}</p>
                </div>
            </div>

            {/* Tokens Section */}
            <div className="mb-4">
                <div className="fw-bold mb-2 d-flex justify-content-between align-items-center" style={TABLE_CAPTION_STYLE}>
                    <span>Tokens</span>
                    <i
                        className="bi bi-plus-circle text-primary"
                        style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                        onClick={handleCreateToken}
                        title="Create New Token"
                    />
                </div>
                {tokensError && (
                    <Alert variant="danger" className="mb-2">{tokensError}</Alert>
                )}
                <div style={{ height: '300px', width: '100%' }}>
                    <DataTable<Token>
                        columnDefs={tokenColumnDefs}
                        data={tokens}
                        isLoading={tokensLoading}
                        loadData={loadTokens}
                        noRowsMessage="No tokens found."
                    />
                </div>
            </div>

            {/* Request Data Section */}
            <div>
                <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                    Request Data {rowCount > 0 && `(${rowCount} total)`}
                </div>

                {requestDataError && (
                    <Alert variant="danger" className="mb-2">{requestDataError}</Alert>
                )}

                <div style={{ height: '600px', width: '100%' }}>
                    <DataTable<RequestData>
                        columnDefs={requestDataColumnDefs}
                        data={requestData}
                        isLoading={requestDataLoading}
                        loadData={loadRequestData}
                        noRowsMessage="No request data found."
                    />
                </div>
            </div>

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
