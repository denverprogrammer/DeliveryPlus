import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ColDef, ICellRendererParams, GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getCampaigns, deleteCampaign } from '../services/api';
import type { Campaign } from '../types/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import 'bootstrap-icons/font/bootstrap-icons.css';

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

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this campaign?')) {
            return;
        }
        try {
            await deleteCampaign(id);
            // Reload data after delete
            const response = await getCampaigns();
            setCampaigns(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete campaign');
        }
    };

    const ActionsCellRenderer = (params: ICellRendererParams<Campaign>) => {
        const campaign = params.data;
        if (!campaign) return null;
        
        return (
            <div className="d-flex gap-2">
                <i
                    className="bi bi-eye text-info"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => navigate(`${ROUTES.CAMPAIGNS}/${campaign.id}`)}
                    title="View"
                />
                <i
                    className="bi bi-pencil text-primary"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => navigate(`${ROUTES.CAMPAIGNS}/${campaign.id}/edit`)}
                    title="Edit"
                />
                <i
                    className="bi bi-trash text-danger"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => handleDelete(campaign.id)}
                    title="Delete"
                />
            </div>
        );
    };

    const columnDefs: ColDef<Campaign>[] = useMemo(() => [
        { field: 'name', headerName: 'Name', sortable: true, filter: true },
        { field: 'campaign_type', headerName: 'Type', sortable: true, filter: true },
        { field: 'description', headerName: 'Description', sortable: true, filter: true },
        { field: 'landing_page_url', headerName: 'Landing Page', sortable: true, filter: true },
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
