import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ColDef, ICellRendererParams, GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getTracking, deleteTracking } from '../services/api';
import type { TrackingListItem } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES, NOT_AVAILABLE } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import 'bootstrap-icons/font/bootstrap-icons.css';

const TrackingList = () => {
    const navigate = useNavigate();
    const [tracking, setTracking] = useState<TrackingListItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadData = useCallback(async (_pagination: PaginationParams, _api: GridApi<TrackingListItem>) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await getTracking();
            setTracking(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load tracking');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this tracking record?')) {
            return;
        }
        try {
            await deleteTracking(id);
            // Reload data after delete
            const response = await getTracking();
            setTracking(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete tracking');
        }
    };

    const handleView = (record: TrackingListItem) => {
        navigate(`${ROUTES.TRACKING}/${record.id}`);
    };

    const handleEdit = (record: TrackingListItem) => {
        navigate(`${ROUTES.TRACKING}/${record.id}/edit`);
    };

    const ActionsCellRenderer = (params: ICellRendererParams<TrackingListItem>) => {
        const record = params.data;
        if (!record) return null;
        
        return (
            <div className="d-flex gap-2">
                <i
                    className="bi bi-eye text-info"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => handleView(record)}
                    title="View"
                />
                <i
                    className="bi bi-pencil text-primary"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => handleEdit(record)}
                    title="Edit"
                />
                <i
                    className="bi bi-trash text-danger"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => handleDelete(record.id)}
                    title="Delete"
                />
            </div>
        );
    };

    const columnDefs: ColDef<TrackingListItem>[] = useMemo(() => [
        {
            headerName: 'Campaign',
            valueGetter: (params) => params.data?.campaign?.name || NOT_AVAILABLE,
            sortable: true,
            filter: true,
        },
        {
            headerName: 'Recipient',
            valueGetter: (params) => params.data?.recipient?.full_name || NOT_AVAILABLE,
            sortable: true,
            filter: true,
        },
        {
            field: 'count_requests',
            headerName: 'Request Count',
            valueGetter: (params) => params.data?.count_requests || 0,
            sortable: true,
            filter: true,
        },
        {
            headerName: 'Actions',
            cellRenderer: ActionsCellRenderer,
            sortable: false,
            filter: false,
            pinned: 'right',
            width: 120,
            suppressSizeToFit: true,
        },
    ], []);

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <div className="p-0 fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                <div className="d-flex justify-content-between align-items-center">
                    <span>Tracking</span>
                    <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.TRACKING}/add`)}>
                        Add Tracking
                    </Button>
                </div>
            </div>
            <div style={{ height: '600px', width: '100%' }}>
                <DataTable<TrackingListItem>
                    columnDefs={columnDefs}
                    data={tracking}
                    isLoading={isLoading}
                    loadData={loadData}
                    noRowsMessage="No tracking records found."
                />
            </div>
        </div>
    );
};

export default TrackingList;
