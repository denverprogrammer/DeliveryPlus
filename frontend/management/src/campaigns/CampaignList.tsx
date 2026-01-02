import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getCampaigns, deleteCampaign } from '../services/api';
import type { Campaign } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import { useActionHandlers } from '../utils/listHandlers';
import { useColumnDefs } from '../hooks/useColumnDefs';

const CampaignList = () => {
    const navigate = useNavigate();
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadData = useCallback(async (_pagination: PaginationParams, _api: GridApi<Campaign>) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await getCampaigns();
            setCampaigns(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load campaigns');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const { handleView, handleEdit, handleDelete } = useActionHandlers<Campaign>({
        baseRoute: ROUTES.CAMPAIGNS,
        onDelete: deleteCampaign,
        onDeleteSuccess: async () => {
            const response = await getCampaigns();
            setCampaigns(response.results);
        },
        deleteConfirmMessage: 'Are you sure you want to delete this campaign?',
    });

    const columnDefs = useColumnDefs<Campaign>('campaignList', { view: handleView, edit: handleEdit, delete: handleDelete });

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <div className="p-0 fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                <div className="d-flex justify-content-between align-items-center">
                    <span>Campaigns</span>
                    <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.CAMPAIGNS}/add`)}>
                        Add Campaign
                    </Button>
                </div>
            </div>
            <div style={{ height: '600px', width: '100%' }}>
                <DataTable<Campaign>
                    columnDefs={columnDefs}
                    data={campaigns}
                    isLoading={isLoading}
                    loadData={loadData}
                    noRowsMessage="No campaigns data found."
                />
            </div>
        </div>
    );
};

export default CampaignList;
