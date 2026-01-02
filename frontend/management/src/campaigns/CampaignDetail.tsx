import { useEffect, useState } from 'react';
import { Table, Alert, Button } from 'react-bootstrap';
import { AgGridReact } from 'ag-grid-react';
import { getCampaign } from '../services/api';
import type { Campaign } from '../types/api';
import { TABLE_CAPTION_STYLE, NOT_AVAILABLE } from '../constants/ui';
import { isNonEmptyArray } from '../utils/typeGuards';
import { useParsedParam } from '../utils/params';
import { defaultColDef, getRowClass } from '../components/DataTable';
import { useNavigator } from '../utils/routes';

const CampaignDetail = () => {
    const navigator = useNavigator();
    const [campaignId] = useParsedParam('id');
    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (campaignId !== null) {
            loadCampaign();
        } else {
            setError('Invalid campaign ID');
            setIsLoading(false);
        }
    }, [campaignId]);

    const loadCampaign = async () => {
        if (campaignId === null) {
            return;
        }
        try {
            setIsLoading(true);
            const response = await getCampaign(campaignId);
            setCampaign(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load campaign');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    if (!campaign) {
        return <Alert variant="warning">Campaign not found</Alert>;
    }


    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>Campaign Details</h3>
                <div>
                    <Button
                        variant="primary"
                        size="sm"
                        onClick={() => navigator.sendToEditCampaign(campaign.id)}
                        className="me-2"
                    >
                        Edit
                    </Button>
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => navigator.sendToCampaigns()}
                    >
                        Back to List
                    </Button>
                </div>
            </div>

            <div className="row mb-4">
                <div className="col-md-6">
                    <Table striped bordered hover>
                        <tbody>
                            <tr>
                                <th className="w-25">ID</th>
                                <td>{campaign.id}</td>
                            </tr>
                            <tr>
                                <th>Name</th>
                                <td>{campaign.name}</td>
                            </tr>
                            <tr>
                                <th>Type</th>
                                <td>{campaign.campaign_type}</td>
                            </tr>
                            <tr>
                                <th>Description</th>
                                <td>{campaign.description || NOT_AVAILABLE}</td>
                            </tr>
                            <tr>
                                <th>Landing Page URL</th>
                                <td>
                                    {campaign.landing_page_url ? (
                                        <a href={campaign.landing_page_url} target="_blank" rel="noopener noreferrer">
                                            {campaign.landing_page_url}
                                        </a>
                                    ) : (
                                        NOT_AVAILABLE
                                    )}
                                </td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
                <div className="col-md-6">
                    <Table striped bordered hover>
                        <tbody>
                            <tr>
                                <th className="w-25">IP Precedence</th>
                                <td>{campaign.ip_precedence || NOT_AVAILABLE}</td>
                            </tr>
                            <tr>
                                <th>Location Precedence</th>
                                <td>{campaign.location_precedence || NOT_AVAILABLE}</td>
                            </tr>
                            <tr>
                                <th>Locale Precedence</th>
                                <td>{campaign.locale_precedence || NOT_AVAILABLE}</td>
                            </tr>
                            <tr>
                                <th>Browser Precedence</th>
                                <td>{campaign.browser_precedence || NOT_AVAILABLE}</td>
                            </tr>
                            <tr>
                                <th>Time Precedence</th>
                                <td>{campaign.time_precedence || NOT_AVAILABLE}</td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
            </div>

            {/* Tracking Configuration */}
            <div className="mb-4">
                <h4 className="mb-3">Tracking Configuration</h4>
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>IP Tracking</div>
                        {isNonEmptyArray(campaign.ip_tracking) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.ip_tracking.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={defaultColDef}
                                    getRowClass={getRowClass}
                                    animateRows={true}
                                    pagination={true}
                                    paginationPageSize={20}
                                    paginationPageSizeSelector={[10, 20, 50, 100]}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No IP tracking configured</p>
                        )}
                    </div>
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>Location Tracking</div>
                        {isNonEmptyArray(campaign.location_tracking) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.location_tracking.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={{ resizable: true }}
                                    animateRows={true}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No location tracking configured</p>
                        )}
                    </div>
                </div>
                <div className="row mt-3">
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>Locale Tracking</div>
                        {isNonEmptyArray(campaign.locale_tracking) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.locale_tracking.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={{ resizable: true }}
                                    animateRows={true}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No locale tracking configured</p>
                        )}
                    </div>
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>Browser Tracking</div>
                        {isNonEmptyArray(campaign.browser_tracking) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.browser_tracking.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={{ resizable: true }}
                                    animateRows={true}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No browser tracking configured</p>
                        )}
                    </div>
                </div>
                <div className="row mt-3">
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>Time Tracking</div>
                        {isNonEmptyArray(campaign.time_tracking) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.time_tracking.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={{ resizable: true }}
                                    animateRows={true}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No time tracking configured</p>
                        )}
                    </div>
                    <div className="col-md-6 mb-3">
                        <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>Publishing Type</div>
                        {isNonEmptyArray(campaign.publishing_type) ? (
                            <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
                                <AgGridReact
                                    rowData={campaign.publishing_type.map((item, index) => ({ id: index, value: item }))}
                                    columnDefs={[{ field: 'value', headerName: 'Value', sortable: true, filter: true }]}
                                    defaultColDef={{ resizable: true }}
                                    animateRows={true}
                                />
                            </div>
                        ) : (
                            <p className="text-muted">No publishing types configured</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Tracking Pixel */}
            {campaign.tracking_pixel && (
                <div className="mb-4">
                    <h4 className="mb-3">Tracking Pixel</h4>
                    <div className="bg-light p-3 rounded">
                        <pre className="m-0" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {campaign.tracking_pixel}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampaignDetail;
