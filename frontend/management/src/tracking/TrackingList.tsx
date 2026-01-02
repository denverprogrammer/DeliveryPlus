import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getTracking, deleteTracking } from '../services/api';
import type { TrackingListItem } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import { useActionHandlers } from '../utils/listHandlers';
import { useColumnDefs } from '../hooks/useColumnDefs';

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

    const { handleView, handleEdit, handleDelete } = useActionHandlers<TrackingListItem>({
        baseRoute: ROUTES.TRACKING,
        onDelete: deleteTracking,
        onDeleteSuccess: async () => {
            const response = await getTracking();
            setTracking(response.results);
        },
        deleteConfirmMessage: 'Are you sure you want to delete this tracking record?',
    });

    const columnDefs = useColumnDefs<TrackingListItem>('trackingList', { view: handleView, edit: handleEdit, delete: handleDelete });

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
