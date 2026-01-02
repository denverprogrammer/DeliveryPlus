import { useState, useCallback } from 'react';
import { GridApi } from 'ag-grid-community';
import { Alert, Button } from 'react-bootstrap';
import { getRecipients } from '../services/api';
import type { Recipient } from '../types/api';
import { TABLE_CAPTION_STYLE } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import { useColumnDefs } from '../hooks/useColumnDefs';
import { useNavigator } from '../utils/routes';

const RecipientList = () => {
    const navigator = useNavigator();
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

    const handleEdit = useCallback((recipient: Recipient) => {
        navigator.sendToEditRecipient(recipient.id);
    }, [navigator]);

    const columnDefs = useColumnDefs<Recipient>('recipientList', { edit: handleEdit });

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <div className="p-0 fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                <div className="d-flex justify-content-between align-items-center">
                    <span>Recipients</span>
                    <Button variant="primary" size="sm" onClick={() => navigator.sendToAddRecipient()}>
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
