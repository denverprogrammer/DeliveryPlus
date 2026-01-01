import { useEffect, useState, useMemo, useCallback } from 'react';
import { Alert } from 'react-bootstrap';
import { ColDef, ICellRendererParams, GridApi } from 'ag-grid-community';
import { getTrackingRecord, getRequestDataList, getTokenList, disableToken, reactivateToken, createToken } from '../services/api';
import type { TrackingDetail, Token, RequestData } from '../types/api';
import RequestDataModal from '../RequestDataModal';
import { TABLE_CAPTION_STYLE, NOT_AVAILABLE } from '../constants/ui';
import { useParsedParam } from '../utils/params';
import DataTable, { DateTimeCellRenderer } from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { formatDate } from '../utils/formatting';

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

    const ViewCellRenderer = (params: ICellRendererParams<RequestData>) => {
        const req = params.data;
        if (!req) return null;
        return (
            <i
                className="bi bi-eye text-info"
                style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                onClick={() => {
                    setSelectedRequestDataId(req.id);
                    setShowModal(true);
                }}
                title="View"
            />
        );
    };

    const handleDisableToken = async (tokenId: number) => {
        if (!window.confirm('Are you sure you want to disable this token?')) {
            return;
        }
        try {
            await disableToken(tokenId);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to disable token');
        }
    };

    const handleReactivateToken = async (tokenId: number) => {
        try {
            await reactivateToken(tokenId);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to reactivate token');
        }
    };

    const handleCreateToken = async () => {
        if (trackingId === null) return;
        try {
            await createToken(trackingId);
            loadTracking(); // Reload tracking to refresh tokens
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create token');
        }
    };

    const TokenActionsCellRenderer = (params: ICellRendererParams<Token>) => {
        const token = params.data;
        if (!token) return null;
        
        const isActive = token.status === 'active';
        const isInactive = token.status === 'inactive';
        
        return (
            <div className="d-flex gap-2">
                {isActive && (
                    <i
                        className="bi bi-x-circle text-warning"
                        style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                        onClick={() => handleDisableToken(token.id)}
                        title="Disable"
                    />
                )}
                {isInactive && (
                    <i
                        className="bi bi-arrow-clockwise text-success"
                        style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                        onClick={() => handleReactivateToken(token.id)}
                        title="Reactivate"
                    />
                )}
            </div>
        );
    };

    const columnDefs: ColDef<RequestData>[] = useMemo(() => [
        {
            field: 'server_timestamp',
            headerName: 'Server Timestamp',
            cellRenderer: DateTimeCellRenderer,
            sortable: true,
            filter: 'agDateColumnFilter',
            filterParams: {
                comparator: (filterLocalDateAtMidnight: Date, cellValue: string) => {
                    if (!cellValue) return 0;
                    const cellDate = new Date(cellValue);
                    if (cellDate < filterLocalDateAtMidnight) {
                        return -1;
                    } else if (cellDate > filterLocalDateAtMidnight) {
                        return 1;
                    } else {
                        return 0;
                    }
                },
            },
        },
        { field: 'data_type', headerName: 'Type', sortable: true, filter: 'agTextColumnFilter', width: 100, suppressSizeToFit: true },
        { field: 'http_method', headerName: 'Method', sortable: true, filter: 'agTextColumnFilter', width: 100, suppressSizeToFit: true },
        { field: 'ip_address', headerName: 'IP Address', sortable: true, filter: 'agTextColumnFilter', width: 130, suppressSizeToFit: true },
        { field: 'os', headerName: 'OS', sortable: true, filter: 'agTextColumnFilter' },
        { field: 'browser', headerName: 'Browser', sortable: true, filter: 'agTextColumnFilter', width: 120, suppressSizeToFit: true },
        { field: 'platform', headerName: 'Platform', sortable: true, filter: 'agTextColumnFilter', width: 120, suppressSizeToFit: true },
        { field: 'locale', headerName: 'Locale', sortable: true, filter: 'agTextColumnFilter', width: 100, suppressSizeToFit: true },
        {
            field: 'client_time',
            headerName: 'Client Timestamp',
            cellRenderer: DateTimeCellRenderer,
            sortable: true,
            filter: 'agDateColumnFilter',
            filterParams: {
                comparator: (filterLocalDateAtMidnight: Date, cellValue: string) => {
                    if (!cellValue) return 0;
                    const cellDate = new Date(cellValue);
                    if (cellDate < filterLocalDateAtMidnight) {
                        return -1;
                    } else if (cellDate > filterLocalDateAtMidnight) {
                        return 1;
                    } else {
                        return 0;
                    }
                },
            },
        },
        {
            headerName: 'Actions',
            cellRenderer: ViewCellRenderer,
            sortable: false,
            filter: false,
            pinned: 'right',
            width: 100,
            suppressSizeToFit: true,
        },
    ], []);


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

    const tokenColumnDefs: ColDef<Token>[] = useMemo(() => [
        { field: 'value', headerName: 'Value', sortable: true, filter: true },
        { field: 'status', headerName: 'Status', sortable: true, filter: true, width: 100, suppressSizeToFit: true },
        {
            field: 'created_on',
            headerName: 'Created',
            valueGetter: (params) => formatDate(params?.data?.created_on) ?? NOT_AVAILABLE,
            sortable: true,
            filter: true,
        },
        {
            field: 'last_used',
            headerName: 'Last Used',
            valueGetter: (params) => formatDate(params?.data?.last_used) ?? NOT_AVAILABLE,
            sortable: true,
            filter: true,
        },
        {
            headerName: 'Used',
            valueGetter: (params) => params.data?.used || 0,
            sortable: true,
            filter: true,
            width: 80,
            suppressSizeToFit: true,
        },
        {
            headerName: 'Actions',
            cellRenderer: TokenActionsCellRenderer,
            sortable: false,
            filter: false,
            pinned: 'right',
            width: 100,
            suppressSizeToFit: true,
        },
    ], [tracking?.count_requests]);


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
                        columnDefs={columnDefs}
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
