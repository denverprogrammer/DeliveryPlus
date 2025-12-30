import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Alert, Form, Pagination } from 'react-bootstrap';
import { getTrackingRecord, getRequestDataList, type RequestDataFilters } from '../shared/services/api';
import type { Tracking, Token, RequestData } from '../shared/types/api';
import RequestDataModal from './RequestDataModal';

const TrackingDetail = () => {
    const { id } = useParams<{ id: string }>();
    const [tracking, setTracking] = useState<Tracking | null>(null);
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
        tracking_id: parseInt(id || '0'),
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
        if (id) {
            loadTracking();
        }
    }, [id]);

    useEffect(() => {
        if (tracking?.id) {
            // Debounce filter changes
            const timeoutId = setTimeout(() => {
                loadRequestData();
            }, 300);
            return () => clearTimeout(timeoutId);
        }
    }, [tracking?.id, filters]);

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
        try {
            setIsLoading(true);
            const response = await getTrackingRecord(parseInt(id!));
            setTracking(response);
            // Update filters with tracking ID
            setFilters(prev => ({ ...prev, tracking_id: response.id }));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    };

    const loadRequestData = async () => {
        if (!tracking?.id) return;
        
        try {
            setRequestDataLoading(true);
            setRequestDataError(null);
            const response = await getRequestDataList({
                ...filters,
                tracking_id: tracking.id,
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
        const unsortedStyle = { fontSize: '1.2em', fontWeight: 'bold' };
        const sortedStyle = { fontSize: '1.2em', fontWeight: 'bold' };
        if (sortColumn !== column) {
            return <span style={unsortedStyle}> ▲▼</span>;
        }
        if (sortDirection === 'asc') {
            return <span style={sortedStyle}> ▲</span>;
        }
        if (sortDirection === 'desc') {
            return <span style={sortedStyle}> ▼</span>;
        }
        return <span style={unsortedStyle}> ▲▼</span>;
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

    const tokens = tracking.tokens || [];

    return (
        <div>
            <h3 className="mb-3">Tracking Details</h3>
            <div className="row mb-4">
                <div className="col-md-6">
                    <p><strong>Campaign:</strong> {tracking.campaign_name}</p>
                    <p><strong>Recipient:</strong> {tracking.recipient_name || 'N/A'}</p>
                </div>
                <div className="col-md-6">
                    <p><strong>Request Count:</strong> {tracking.count_requests || 0}</p>
                </div>
            </div>

            {/* Tokens Section */}
            <div className="mb-4">
                {tokens.length > 0 ? (
                    <Table striped bordered hover style={{ captionSide: 'top' }}>
                        <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>Tokens</caption>
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
                <Table striped bordered hover size="sm" style={{ captionSide: 'top' }}>
                    <caption style={{ captionSide: 'top', fontWeight: 'bold', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
                        Request Data {pagination.count > 0 && `(${pagination.count} total)`}
                    </caption>
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'center' }}>
                                ID
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('server_timestamp')}>
                                Timestamp {getSortIcon('server_timestamp')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('data_type')}>
                                Type {getSortIcon('data_type')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('http_method')}>
                                Method {getSortIcon('http_method')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('ip_address')}>
                                IP Address {getSortIcon('ip_address')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('os')}>
                                OS {getSortIcon('os')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('browser')}>
                                Browser {getSortIcon('browser')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('platform')}>
                                Platform {getSortIcon('platform')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('locale')}>
                                Locale {getSortIcon('locale')}
                            </th>
                            <th style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => handleSort('client_time')}>
                                Client Time {getSortIcon('client_time')}
                            </th>
                        </tr>
                        {/* Filters Row */}
                        <tr>
                            <td></td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    type="date"
                                    value={filters.server_timestamp || ''}
                                    onChange={(e) => handleFilterChange('server_timestamp', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="Data Type"
                                    value={filters.data_type || ''}
                                    onChange={(e) => handleFilterChange('data_type', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="HTTP Method"
                                    value={filters.http_method || ''}
                                    onChange={(e) => handleFilterChange('http_method', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="IP Address"
                                    value={filters.ip_address || ''}
                                    onChange={(e) => handleFilterChange('ip_address', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="OS"
                                    value={filters.os || ''}
                                    onChange={(e) => handleFilterChange('os', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="Browser"
                                    value={filters.browser || ''}
                                    onChange={(e) => handleFilterChange('browser', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="Platform"
                                    value={filters.platform || ''}
                                    onChange={(e) => handleFilterChange('platform', e.target.value)}
                                />
                            </td>
                            <td>
                                <Form.Control
                                    size="sm"
                                    placeholder="Locale"
                                    value={filters.locale || ''}
                                    onChange={(e) => handleFilterChange('locale', e.target.value)}
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
                        ) : requestData.length > 0 ? (
                            requestData.map((req: RequestData) => (
                                <tr key={req.id}>
                                    <td>
                                        <button
                                            className="btn btn-link p-0"
                                            style={{ textDecoration: 'underline', border: 'none', background: 'none', color: '#0d6efd' }}
                                            onClick={() => {
                                                setSelectedRequestDataId(req.id);
                                                setShowModal(true);
                                            }}
                                        >
                                            {req.id}
                                        </button>
                                    </td>
                                    <td>{formatDateTime(req.server_timestamp)}</td>
                                    <td>{req.data_type || 'N/A'}</td>
                                    <td>{req.http_method || 'N/A'}</td>
                                    <td>{req.ip_address || 'N/A'}</td>
                                    <td>{req.os || 'N/A'}</td>
                                    <td>{req.browser || 'N/A'}</td>
                                    <td>{req.platform || 'N/A'}</td>
                                    <td>{req.locale || 'N/A'}</td>
                                    <td>{req.client_time ? formatDateTime(req.client_time) : <><span>N/A</span></>}</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={10} className="text-center text-muted">No request data found.</td>
                            </tr>
                        )}
                    </tbody>
                </Table>
                
                {/* Pagination and Page Size */}
                <div className="d-flex justify-content-between align-items-center mt-3">
                    <Form.Group className="d-flex align-items-center mb-0">
                        <Form.Label className="me-2 mb-0">Page Size:</Form.Label>
                        <Form.Select
                            size="sm"
                            style={{ width: 'auto' }}
                            value={filters.page_size || 20}
                            onChange={(e) => setFilters(prev => ({ ...prev, page_size: parseInt(e.target.value), page: 1 }))}
                        >
                            <option value="5">5</option>
                            <option value="10">10</option>
                            <option value="20">20</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                        </Form.Select>
                    </Form.Group>
                    
                    {pagination.total_pages > 1 && (
                        <Pagination className="mb-0">
                            <Pagination.First 
                                disabled={pagination.page === 1}
                                onClick={() => handlePageChange(1)}
                            />
                            <Pagination.Prev 
                                disabled={pagination.page === 1}
                                onClick={() => handlePageChange(pagination.page - 1)}
                            />
                            {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                                let pageNum;
                                if (pagination.total_pages <= 5) {
                                    pageNum = i + 1;
                                } else if (pagination.page <= 3) {
                                    pageNum = i + 1;
                                } else if (pagination.page >= pagination.total_pages - 2) {
                                    pageNum = pagination.total_pages - 4 + i;
                                } else {
                                    pageNum = pagination.page - 2 + i;
                                }
                                return (
                                    <Pagination.Item
                                        key={pageNum}
                                        active={pageNum === pagination.page}
                                        onClick={() => handlePageChange(pageNum)}
                                    >
                                        {pageNum}
                                    </Pagination.Item>
                                );
                            })}
                            <Pagination.Next 
                                disabled={pagination.page === pagination.total_pages}
                                onClick={() => handlePageChange(pagination.page + 1)}
                            />
                            <Pagination.Last 
                                disabled={pagination.page === pagination.total_pages}
                                onClick={() => handlePageChange(pagination.total_pages)}
                            />
                        </Pagination>
                    )}
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
