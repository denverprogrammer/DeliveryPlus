import { useMemo } from 'react';
import { DateTimeCellRenderer, createActionsCellRenderer } from '../components/DataTable';
import { ViewAction, EditAction, DeleteAction, ReactivateAction, DisableAction } from '../components/Actions';
import { formatDate } from '../utils/formatting';
import { NOT_AVAILABLE } from '../constants/ui';
import { isActiveStatus, isInactiveStatus } from '../utils/typeGuards';
import type { User, Campaign, TrackingListItem, Recipient, RequestData, Token } from '../types/api';
import { ColDef, ICellRendererParams } from 'ag-grid-community';

// Date filter comparator helper
const dateFilterComparator = (filterLocalDateAtMidnight: Date, cellValue: string) => {
    if (!cellValue) return 0;
    const cellDate = new Date(cellValue);
    if (cellDate < filterLocalDateAtMidnight) {
        return -1;
    } else if (cellDate > filterLocalDateAtMidnight) {
        return 1;
    } else {
        return 0;
    }
};

type GridType = 
    | 'userList'
    | 'campaignList'
    | 'trackingList'
    | 'recipientList'
    | 'requestData'
    | 'token';

type Handler = (...args: any[]) => void;

export const useColumnDefs = <T,>(
    gridType: GridType,
    handlers: Record<string, Handler>
): ColDef<T>[] => {
    return useMemo(() => {
        switch (gridType) {
            case 'userList': {
                const { view: handleView, edit: handleEdit, delete: handleDelete } = handlers as {
                    view: (user: User) => void;
                    edit: (user: User) => void;
                    delete: (user: User) => void;
                };
                const renderActions = (user: User) => [
                    <ViewAction key="view" handler={() => handleView(user)} />,
                    <EditAction key="edit" handler={() => handleEdit(user)} />,
                    <DeleteAction key="delete" handler={() => handleDelete(user)} />,
                ];

                return [
                    { field: 'username', headerName: 'Username', sortable: true, filter: true },
                    { field: 'email', headerName: 'Email', sortable: true, filter: true },
                    {
                        headerName: 'Name',
                        valueGetter: (params: ICellRendererParams<User>) => `${params.data?.first_name || ''} ${params.data?.last_name || ''}`.trim(),
                        sortable: true,
                        filter: true,
                    },
                    {
                        field: 'is_active',
                        headerName: 'Active',
                        valueGetter: (params:ICellRendererParams<User>) => params.data?.is_active ? 'Yes' : 'No',
                        sortable: true,
                        filter: true,
                    },
                    {
                        field: 'is_staff',
                        headerName: 'Staff',
                        valueGetter: (params: ICellRendererParams<User>) => params.data?.is_staff ? 'Yes' : 'No',
                        sortable: true,
                        filter: true,
                    },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 120,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            case 'campaignList': {
                const { view: handleView, edit: handleEdit, delete: handleDelete } = handlers as {
                    view: (campaign: Campaign) => void;
                    edit: (campaign: Campaign) => void;
                    delete: (campaign: Campaign) => void;
                };
                const renderActions = (campaign: Campaign) => [
                    <ViewAction key="view" handler={() => handleView(campaign)} />,
                    <EditAction key="edit" handler={() => handleEdit(campaign)} />,
                    <DeleteAction key="delete" handler={() => handleDelete(campaign)} />,
                ];

                return [
                    { field: 'name', headerName: 'Name', sortable: true, filter: true },
                    { field: 'campaign_type', headerName: 'Type', sortable: true, filter: true },
                    { field: 'description', headerName: 'Description', sortable: true, filter: true },
                    { field: 'landing_page_url', headerName: 'Landing Page', sortable: true, filter: true },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 120,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            case 'trackingList': {
                const { view: handleView, edit: handleEdit, delete: handleDelete } = handlers as {
                    view: (record: TrackingListItem) => void;
                    edit: (record: TrackingListItem) => void;
                    delete: (record: TrackingListItem) => void;
                };
                const renderActions = (record: TrackingListItem) => [
                    <ViewAction key="view" handler={() => handleView(record)} />,
                    <EditAction key="edit" handler={() => handleEdit(record)} />,
                    <DeleteAction key="delete" handler={() => handleDelete(record)} />,
                ];

                return [
                    {
                        headerName: 'Campaign',
                        valueGetter: (params: ICellRendererParams<TrackingListItem>) => params.data?.campaign?.name || NOT_AVAILABLE,
                        sortable: true,
                        filter: true,
                    },
                    {
                        headerName: 'Recipient',
                        valueGetter: (params: ICellRendererParams<TrackingListItem>) => params.data?.recipient?.full_name || NOT_AVAILABLE,
                        sortable: true,
                        filter: true,
                    },
                    {
                        field: 'count_requests',
                        headerName: 'Request Count',
                        valueGetter: (params: ICellRendererParams<TrackingListItem>) => params.data?.count_requests || 0,
                        sortable: true,
                        filter: true,
                    },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 120,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            case 'recipientList': {
                const { edit: handleEdit } = handlers as {
                    edit: (recipient: Recipient) => void;
                };
                const renderActions = (recipient: Recipient) => [
                    <EditAction key="edit" handler={() => handleEdit(recipient)} />,
                ];

                return [
                    {
                        headerName: 'Name',
                        valueGetter: (params: ICellRendererParams<Recipient>) => `${params.data?.first_name || ''} ${params.data?.last_name || ''}`.trim(),
                        sortable: true,
                        filter: true,
                    },
                    { field: 'email', headerName: 'Email', sortable: true, filter: true },
                    {
                        field: 'status',
                        headerName: 'Status',
                        valueGetter: (params: ICellRendererParams<Recipient>) => params.data?.status || NOT_AVAILABLE,
                        sortable: true,
                        filter: true,
                    },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 80,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            case 'requestData': {
                const { view: handleView } = handlers as {
                    view: (requestData: RequestData) => void;
                };
                const renderActions = (requestData: RequestData) => [
                    <ViewAction key="view" handler={() => handleView(requestData)} />,
                ];

                return [
                    {
                        field: 'server_timestamp',
                        headerName: 'Server Timestamp',
                        cellRenderer: DateTimeCellRenderer,
                        sortable: true,
                        filter: 'agDateColumnFilter',
                        filterParams: {
                            comparator: dateFilterComparator,
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
                            comparator: dateFilterComparator,
                        },
                    },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 100,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            case 'token': {
                const { disable: handleDisable, reactivate: handleReactivate } = handlers as {
                    disable: (token: Token) => void;
                    reactivate: (token: Token) => void;
                };
                const renderActions = (token: Token) => {
                    const actions = [];
                    
                    if (isActiveStatus(token.status)) {
                        actions.push(
                            <DisableAction key="disable" handler={() => handleDisable(token)} />
                        );
                    }
                    
                    if (isInactiveStatus(token.status)) {
                        actions.push(
                            <ReactivateAction key="reactivate" handler={() => handleReactivate(token)} />
                        );
                    }
                    
                    return actions;
                };

                return [
                    { field: 'value', headerName: 'Value', sortable: true, filter: true },
                    { field: 'status', headerName: 'Status', sortable: true, filter: true, width: 100, suppressSizeToFit: true },
                    {
                        field: 'created_on',
                        headerName: 'Created',
                        valueGetter: (params: ICellRendererParams<Token>) => formatDate(params?.data?.created_on) ?? NOT_AVAILABLE,
                        sortable: true,
                        filter: true,
                    },
                    {
                        field: 'last_used',
                        headerName: 'Last Used',
                        valueGetter: (params: ICellRendererParams<Token>) => formatDate(params?.data?.last_used) ?? NOT_AVAILABLE,
                        sortable: true,
                        filter: true,
                    },
                    {
                        headerName: 'Used',
                        valueGetter: (params: ICellRendererParams<Token>) => params.data?.used || 0,
                        sortable: true,
                        filter: true,
                        width: 80,
                        suppressSizeToFit: true,
                    },
                    {
                        headerName: 'Actions',
                        cellRenderer: createActionsCellRenderer(renderActions),
                        sortable: false,
                        filter: false,
                        pinned: 'right',
                        width: 100,
                        suppressSizeToFit: true,
                    },
                ] as ColDef<T>[];
            }

            default:
                throw new Error(`Unknown grid type: ${gridType}`);
        }
    }, [gridType, ...Object.values(handlers)]);
};

