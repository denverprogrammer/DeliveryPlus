import { useRef, useCallback, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GridApi, FilterChangedEvent, SortChangedEvent, PaginationChangedEvent, RowClassParams, ICellRendererParams } from 'ag-grid-community';
import { DEBOUNCE_DELAY, NOT_AVAILABLE } from '../constants/ui';
import type { PaginationParams } from '../types/api';
import { formatDateTime } from '../utils/formatting';
import { useGridTheme } from '../contexts/ThemeContext';

/**
 * Default column definition for ag-grid tables.
 * Provides resizable, sortable, and filterable columns by default.
 */
export const defaultColDef: ColDef = {
    resizable: true,
    sortable: true,
    filter: true,
};

/**
 * Row class function for ag-grid tables.
 * Provides alternating row colors (even/odd) for better readability.
 */
export const getRowClass = (params: RowClassParams): string => {
    const rowIndex = params.node.rowIndex;
    if (rowIndex === null) return '';
    return rowIndex % 2 === 0 ? 'ag-row-even' : 'ag-row-odd';
};

/**
 * Converts ag-grid sort state to API ordering string.
 * Returns empty string if no sort is applied.
 * Format: "-fieldName" for descending, "fieldName" for ascending.
 */
export const getAgGridSortOrdering = <T,>(api: GridApi<T>): string => {
    const columnState = api.getColumnState();
    const sortedColumn = columnState.find(col => col.sort != null);
    if (!sortedColumn || !sortedColumn.sort) {
        return '';
    }
    return sortedColumn.sort === 'desc' ? `-${sortedColumn.colId}` : sortedColumn.colId || '';
};

/**
 * Gets pagination state from ag-grid API.
 * @param api - The ag-grid API instance
 * @param oneBased - If true, converts page from 0-based to 1-based (default: false)
 * @returns Object with page and pageSize
 */
export const getAgGridPaginationState = <T,>(
    api: GridApi<T>,
    oneBased: boolean = false
): { page: number; pageSize: number } => {
    const page = api.paginationGetCurrentPage();
    const pageSize = api.paginationGetPageSize();
    return {
        page: oneBased ? page + 1 : page,
        pageSize,
    };
};

export interface DataTableProps<T = any> {
    columnDefs: ColDef<T>[];
    data: T[];
    isLoading: boolean;
    loadData: (pagination: PaginationParams, api: GridApi<T>) => Promise<void>;
    paginationPageSize?: number;
    paginationPageSizeSelector?: number[];
    noRowsMessage?: string;
    onGridReady?: (params: { api: GridApi<T> }) => void;
}

const DataTable = <T,>({
    columnDefs,
    data,
    isLoading,
    loadData,
    paginationPageSize = 20,
    paginationPageSizeSelector = [5, 10, 20, 50, 100],
    noRowsMessage = 'No data found.',
    onGridReady: onGridReadyProp,
}: DataTableProps<T>) => {
    const { gridTheme } = useGridTheme();
    const gridRef = useRef<AgGridReact<T>>(null);
    const filterTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const convertDateFilter = (dateValue: Date | string): string | undefined => {
        const date = dateValue instanceof Date ? dateValue : new Date(dateValue);
        if (isNaN(date.getTime())) {
            return undefined;
        }
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    const getPaginationParams = useCallback((api: GridApi<T>): PaginationParams => {
        const { page, pageSize } = getAgGridPaginationState(api, true);
        const ordering = getAgGridSortOrdering(api);
        const filterModel = api.getFilterModel();
        const filters: Record<string, any> = {};

        // Convert ag-grid filter model to API filters
        Object.keys(filterModel).forEach((field) => {
            const filter = filterModel[field];
            
            // Handle date filters
            if (filter.dateFrom) {
                const dateValue = convertDateFilter(filter.dateFrom);
                if (dateValue) {
                    filters[field] = dateValue;
                }
            }
            // Handle text filters
            else if (filter.filter) {
                filters[field] = filter.filter;
            }
        });

        return {
            page,
            page_size: pageSize,
            ordering: ordering || undefined,
            filters: Object.keys(filters).length > 0 ? filters : undefined,
        };
    }, []);

    const onGridReady = useCallback((params: { api: GridApi<T> }) => {
        if (onGridReadyProp) {
            onGridReadyProp(params);
        } else {
            // Auto-load data on grid ready if no custom handler
            const pagination = getPaginationParams(params.api);
            loadData(pagination, params.api);
        }
    }, [loadData, onGridReadyProp, getPaginationParams]);

    const onFilterChanged = useCallback((_event: FilterChangedEvent) => {
        const api = gridRef.current?.api;
        if (!api) return;
        
        // Debounce filter changes
        if (filterTimeoutRef.current) {
            clearTimeout(filterTimeoutRef.current);
        }
        filterTimeoutRef.current = setTimeout(() => {
            api.paginationGoToFirstPage();
            const pagination = getPaginationParams(api);
            loadData(pagination, api);
        }, DEBOUNCE_DELAY);
    }, [loadData, getPaginationParams]);

    const onSortChanged = useCallback((_event: SortChangedEvent) => {
        const api = gridRef.current?.api;
        if (!api) return;
        api.paginationGoToFirstPage();
        const pagination = getPaginationParams(api);
        loadData(pagination, api);
    }, [loadData, getPaginationParams]);

    const onPaginationChanged = useCallback((event: PaginationChangedEvent) => {
        const api = gridRef.current?.api;
        if (!api) return;
        if (event.newPage) {
            const pagination = getPaginationParams(api);
            loadData(pagination, api);
        }
    }, [loadData, getPaginationParams]);

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (filterTimeoutRef.current) {
                clearTimeout(filterTimeoutRef.current);
            }
        };
    }, []);

    return (
        <AgGridReact
            ref={gridRef}
            theme={gridTheme}
            rowData={data}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            getRowClass={getRowClass}
            animateRows={true}
            loading={isLoading}
            noRowsOverlayComponentParams={{ message: noRowsMessage }}
            onGridReady={onGridReady}
            onFilterChanged={onFilterChanged}
            onSortChanged={onSortChanged}
            onPaginationChanged={onPaginationChanged}
            pagination={true}
            paginationPageSize={paginationPageSize}
            paginationPageSizeSelector={paginationPageSizeSelector}
            suppressPaginationPanel={false}
            enableRangeSelection={false}
            suppressMenuHide={false}
        />
    );
};

/**
 * Cell renderer for displaying date and time in separate spans.
 * Formats the date value using formatDateTime and displays "N/A" if the value is invalid.
 */
export const DateTimeCellRenderer = <T,>(params: ICellRendererParams<T>): React.ReactNode => {
    const dateTime = formatDateTime(params.value as string | undefined | null);
    if (!dateTime) return NOT_AVAILABLE;

    return <><span>{dateTime[0]}</span>, <span>{dateTime[1]}</span></>;
};

/**
 * Creates an Actions cell renderer from a renderActions function.
 * The renderActions function should take a row item and return an array of React nodes.
 * 
 * @param renderActions - Function that takes a row item and returns an array of action components
 * @returns A cell renderer function for ag-grid
 */
export const createActionsCellRenderer = <T,>(
    renderActions: (item: T) => React.ReactNode[]
): ((params: ICellRendererParams<T>) => React.ReactNode) => {
    return (params: ICellRendererParams<T>) => {
        const item = params.data;
        if (!item) return null;
        
        const actions = renderActions(item);
        
        return (
            <div className="d-flex gap-2">
                {actions}
            </div>
        );
    };
};

export default DataTable;

