import { useEffect, useState } from 'react';
import { Table, Alert, Form } from 'react-bootstrap';
import { getTrackingRecord, getRequestDataList, type RequestDataFilters } from '../services/api';
import type { TrackingDetail, Token, RequestData } from '../types/api';
import RequestDataModal from '../RequestDataModal';
import PaginationControls from '../components/PaginationControls';
import { TABLE_CAPTION_STYLE, SORT_ICON_STYLE, FILTER_INPUT_MIN_WIDTH, COLORS, DEBOUNCE_DELAY } from '../constants/ui';
import { useParsedParam } from '../utils/params';
import { isNonEmptyArray } from '../utils/typeGuards';

const TrackingDetail = () => {
    const [trackingId] = useParsedParam('id');
    const [tracking, setTracking] = useState<TrackingDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [selectedRequestDataId, setSelectedRequestDataId] = useState<number | null>(null);
    
    // Request data pagination and filtering
    const [requestData, setRequestData] = useState<RequestData[]>([]);
    const [requestDataLoading, setRequestDataLoading] = useState(false);
    const [requestDataError, setRequestDataError] = useState<string | null>(null);
    const [pagination, setPagination] = useState({ count: 0, page: 1, page_size: 20, total_pages: 1 });
    const [filters, setFilters] = useState<RequestDataFilters>({
        tracking_id: trackingId || 0,
        data_type: '',
        http_method: '',
        ip_address: '',
        os: '',
        browser: '',
        platform: '',
        locale: '',
        server_timestamp: '',
        client_time: '',
        page: 1,
        page_size: 20,
        ordering: '',
    });
    const [sortColumn, setSortColumn] = useState<string>('');
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc' | ''>('');

    useEffect(() => {
        if (trackingId !== null) {
            loadTracking();
        } else {
            setError('Invalid tracking ID');
            setIsLoading(false);
        }
    }, [trackingId]);

    useEffect(() => {
        if (trackingId !== null) {
            // Debounce filter changes
            const timeoutId = setTimeout(() => {
                loadRequestData();
            }, DEBOUNCE_DELAY);
            return () => clearTimeout(timeoutId);
        }
    }, [trackingId, filters]);

    // Sync sort state with filters.ordering
    useEffect(() => {
        if (!filters.ordering) {
            setSortColumn('');
            setSortDirection('');
        } else if (filters.ordering.startsWith('-')) {
            setSortColumn(filters.ordering.substring(1));
            setSortDirection('desc');
        } else {
            setSortColumn(filters.ordering);
            setSortDirection('asc');
        }
    }, [filters.ordering]);

    const loadTracking = async () => {
        if (trackingId === null) {
            return;
        }
        try {
            setIsLoading(true);
            const tracking = await getTrackingRecord(trackingId);
            setTracking(tracking);
            // Update filters with tracking ID
            setFilters(prev => ({ ...prev, tracking_id: tracking.id }));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    const loadRequestData = async () => {
        if (trackingId === null) {
            return;
        }
        try {
            setRequestDataLoading(true);
            setRequestDataError(null);
            const response = await getRequestDataList({
                ...filters,
                tracking_id: trackingId,
            });
            
            if ('results' in response && Array.isArray(response.results)) {
                setRequestData(response.results);
                const pageSize = filters.page_size || 20;
                const currentPage = filters.page || 1;
                setPagination({
                    count: response.count || 0,
                    page: currentPage,
                    page_size: pageSize,
                    total_pages: Math.ceil((response.count || 0) / pageSize),
                });
            } else {
                // Fallback if not paginated
                const dataArray = Array.isArray(response) ? response : [];
                setRequestData(dataArray);
                setPagination({
                    count: dataArray.length,
                    page: 1,
                    page_size: filters.page_size || 20,
                    total_pages: 1,
                });
            }
        } catch (err) {
            setRequestDataError(err instanceof Error ? err.message : 'Failed to load request data');
            setRequestData([]);
        } finally {
            setRequestDataLoading(false);
        }
    };

    const handleFilterChange = (field: keyof RequestDataFilters, value: string) => {
        setFilters(prev => ({ ...prev, [field]: value, page: 1 }));
    };

    const handlePageChange = (page: number) => {
        setFilters(prev => ({ ...prev, page }));
    };

    const handleSort = (column: string) => {
        if (sortColumn !== column) {
            // New column - start with ascending
            setSortColumn(column);
            setSortDirection('asc');
            setFilters(prev => ({ ...prev, ordering: column, page: 1 }));
        } else if (sortDirection === 'asc') {
            // Switch to descending
            setSortDirection('desc');
            setFilters(prev => ({ ...prev, ordering: `-${column}`, page: 1 }));
        } else if (sortDirection === 'desc') {
            // Remove sorting
            setSortColumn('');
            setSortDirection('');
            setFilters(prev => ({ ...prev, ordering: '', page: 1 }));
        }
    };

    const getSortIcon = (column: string) => {
        if (sortColumn !== column) {
            return <span className="fw-bold" style={SORT_ICON_STYLE}> ▲▼</span>;
        }
        if (sortDirection === 'asc') {
            return <span className="fw-bold" style={SORT_ICON_STYLE}> ▲</span>;
        }
        if (sortDirection === 'desc') {
            return <span className="fw-bold" style={SORT_ICON_STYLE}> ▼</span>;
        }
        return <span className="fw-bold" style={SORT_ICON_STYLE}> ▲▼</span>;
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch {
            return dateString;
        }
    };

    const formatDateTime = (dateString: string) => {
        if (!dateString) return <><span>N/A</span></>;
        try {
            const date = new Date(dateString);
            const datePart = date.toLocaleDateString();
            const timePart = date.toLocaleTimeString();
            return (
                <>
                    <span>{datePart}</span>, <span>{timePart}</span>
                </>
            );
        } catch {
            return <><span>{dateString}</span></>;
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

    const tokens = tracking.tokens ?? [];

    return (
        <div>
            <h3 className="mb-3">Tracking Details</h3>
            <div className="row mb-4">
                <div className="col-md-6">
                    <p><strong>Campaign:</strong> {tracking.campaign?.name || 'N/A'}</p>
                    <p><strong>Recipient:</strong> {tracking.recipient?.full_name || 'N/A'}</p>
                </div>
                <div className="col-md-6">
                    <p><strong>Request Count:</strong> {tracking.count_requests || 0}</p>
                </div>
            </div>

            {/* Tokens Section */}
            <div className="mb-4">
                {isNonEmptyArray(tokens) ? (
                    <Table striped bordered hover>
                        <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>Tokens</caption>
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
            </div>

            {/* Request Data Section */}
            <div>
                <Table striped bordered hover size="sm">
                    <caption className="fw-bold" style={TABLE_CAPTION_STYLE}>
                        Request Data {pagination.count > 0 && `(${pagination.count} total)`}
                    </caption>
                    <thead>
                        <tr>
                            <th className="text-center" style={{ cursor: 'pointer' }} onClick={() => handleSort('server_timestamp')}>
                                Timestamp {getSortIcon('server_timestamp')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('data_type')}>
                                Type {getSortIcon('data_type')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('http_method')}>
                                Method {getSortIcon('http_method')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('ip_address')}>
                                IP Address {getSortIcon('ip_address')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer' }} onClick={() => handleSort('os')}>
                                OS {getSortIcon('os')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('browser')}>
                                Browser {getSortIcon('browser')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('platform')}>
                                Platform {getSortIcon('platform')}
                            </th>
                            <th className="text-center text-nowrap" style={{ cursor: 'pointer', width: 'auto' }} onClick={() => handleSort('locale')}>
                                Locale {getSortIcon('locale')}
                            </th>
                            <th className="text-center" style={{ cursor: 'pointer' }} onClick={() => handleSort('client_time')}>
                                Client Time {getSortIcon('client_time')}
                            </th>
                            <th className="text-center">
                                ####
                            </th>
                        </tr>
                        {/* Filters Row */}
                        <tr>
                            <td>
                                <Form.Control
                                    size="sm"
                                    type="date"
                                    value={filters.server_timestamp || ''}
                                    onChange={(e) => handleFilterChange('server_timestamp', e.target.value)}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="Data Type"
                                    value={filters.data_type || ''}
                                    onChange={(e) => handleFilterChange('data_type', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.SMALL }}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="HTTP Method"
                                    value={filters.http_method || ''}
                                    onChange={(e) => handleFilterChange('http_method', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.SMALL }}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="IP Address"
                                    value={filters.ip_address || ''}
                                    onChange={(e) => handleFilterChange('ip_address', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.MEDIUM }}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="OS"
                                    value={filters.os || ''}
                                    onChange={(e) => handleFilterChange('os', e.target.value)}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="Browser"
                                    value={filters.browser || ''}
                                    onChange={(e) => handleFilterChange('browser', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.SMALL }}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="Platform"
                                    value={filters.platform || ''}
                                    onChange={(e) => handleFilterChange('platform', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.SMALL }}
                                />
                            </td>
                            <td className="text-nowrap" style={{ width: '1%' }}>
                                <Form.Control
                                    size="sm"
                                    placeholder="Locale"
                                    value={filters.locale || ''}
                                    onChange={(e) => handleFilterChange('locale', e.target.value)}
                                    style={{ width: 'auto', minWidth: FILTER_INPUT_MIN_WIDTH.SMALL }}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    type="date"
                                    value={filters.client_time || ''}
                                    onChange={(e) => handleFilterChange('client_time', e.target.value)}
                                />
                            </td>
                            <td></td>
                        </tr>
                    </thead>
                    <tbody>
                        {requestDataLoading ? (
                            <tr>
                                <td colSpan={10} className="text-center">Loading...</td>
                            </tr>
                        ) : requestDataError ? (
                            <tr>
                                <td colSpan={10} className="text-center text-danger">{requestDataError}</td>
                            </tr>
                        ) : isNonEmptyArray(requestData) ? (
                            requestData.map((req: RequestData) => (
                                <tr key={req.id}>
                                    <td>{formatDateTime(req.server_timestamp)}</td>
                                    <td className="text-nowrap">{req.data_type || 'N/A'}</td>
                                    <td className="text-nowrap">{req.http_method || 'N/A'}</td>
                                    <td className="text-nowrap">{req.ip_address || 'N/A'}</td>
                                    <td className="text-nowrap">{req.os || 'N/A'}</td>
                                    <td className="text-nowrap">{req.browser || 'N/A'}</td>
                                    <td className="text-nowrap">{req.platform || 'N/A'}</td>
                                    <td className="text-nowrap">{req.locale || 'N/A'}</td>
                                    <td>{req.client_time ? formatDateTime(req.client_time) : <><span>N/A</span></>}</td>
                                    <td>
                                        <button
                                            className="btn btn-link p-0 text-decoration-underline border-0 bg-transparent"
                                            style={{ color: COLORS.PRIMARY }}
                                            onClick={() => {
                                                setSelectedRequestDataId(req.id);
                                                setShowModal(true);
                                            }}
                                        >
                                            View
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={10} className="text-center text-muted">No request data found.</td>
                            </tr>
                        )}
                    </tbody>
                </Table>
                
                <PaginationControls
                    pagination={pagination}
                    pageSize={filters.page_size || 20}
                    onPageChange={handlePageChange}
                    onPageSizeChange={(newPageSize) => {
                        setFilters((prev) => ({ ...prev, page_size: newPageSize, page: 1 }));
                    }}
                />
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
