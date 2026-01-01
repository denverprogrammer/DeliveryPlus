import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ColDef, ICellRendererParams, GridApi } from 'ag-grid-community';
import { Alert, Button } from 'react-bootstrap';
import { getRecipients } from '../services/api';
import type { Recipient } from '../types/api';
import { NOT_AVAILABLE, ROUTES, TABLE_CAPTION_STYLE } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import 'bootstrap-icons/font/bootstrap-icons.css';

const RecipientList = () => {
    const navigate = useNavigate();
    const [recipients, setRecipients] = useState<Recipient[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadData = useCallback(async (_pagination: PaginationParams, _api: GridApi<Recipient>) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await getRecipients();
            setRecipients(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load recipients');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const ActionsCellRenderer = (params: ICellRendererParams<Recipient>) => {
        const recipient = params.data;
        if (!recipient) return null;
        
        return (
            <i
                className="bi bi-pencil text-primary"
                style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                onClick={() => navigate(`${ROUTES.RECIPIENTS}/${recipient.id}/edit`)}
                title="Edit"
            />
        );
    };

    const columnDefs: ColDef<Recipient>[] = useMemo(() => [
        {
            headerName: 'Name',
            valueGetter: (params) => `${params.data?.first_name || ''} ${params.data?.last_name || ''}`.trim(),
            sortable: true,
            filter: true,
        },
        { field: 'email', headerName: 'Email', sortable: true, filter: true },
        {
            field: 'status',
            headerName: 'Status',
            valueGetter: (params) => params.data?.status || NOT_AVAILABLE,
            sortable: true,
            filter: true,
        },
        {
            headerName: 'Actions',
            cellRenderer: ActionsCellRenderer,
            sortable: false,
            filter: false,
            pinned: 'right',
            width: 80,
            suppressSizeToFit: true,
        },
    ], []);

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <div className="p-0 fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                <div className="d-flex justify-content-between align-items-center">
                    <span>Recipients</span>
                    <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.RECIPIENTS}/add`)}>
                        Add Recipient
                    </Button>
                </div>
            </div>
            <div style={{ height: '600px', width: '100%' }}>
                <DataTable<Recipient>
                    columnDefs={columnDefs}
                    data={recipients}
                    isLoading={isLoading}
                    loadData={loadData}
                    noRowsMessage="No recipients found."
                />
            </div>
        </div>
    );
};

export default RecipientList;
