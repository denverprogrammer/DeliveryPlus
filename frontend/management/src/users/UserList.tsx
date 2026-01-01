import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ColDef, ICellRendererParams, GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getUsers, deleteUser } from '../services/api';
import { TABLE_CAPTION_STYLE, ROUTES } from '../constants/ui';
import type { User } from '../types/api';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import 'bootstrap-icons/font/bootstrap-icons.css';

const UserList = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState<User[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadData = useCallback(async (_pagination: PaginationParams, _api: GridApi<User>) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await getUsers();
            setUsers(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load users');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this user?')) {
            return;
        }
        try {
            await deleteUser(id);
            // Reload data after delete
            const response = await getUsers();
            setUsers(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete user');
        }
    };

    const ActionsCellRenderer = (params: ICellRendererParams<User>) => {
        const user = params.data;
        if (!user) return null;
        
        return (
            <div className="d-flex gap-2">
                <i
                    className="bi bi-eye text-info"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => navigate(`${ROUTES.USERS}/${user.id}`)}
                    title="View"
                />
                <i
                    className="bi bi-pencil text-primary"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => navigate(`${ROUTES.USERS}/${user.id}/edit`)}
                    title="Edit"
                />
                <i
                    className="bi bi-trash text-danger"
                    style={{ cursor: 'pointer', fontSize: '1.2rem' }}
                    onClick={() => handleDelete(user.id)}
                    title="Delete"
                />
            </div>
        );
    };

    const columnDefs: ColDef<User>[] = useMemo(() => [
        { field: 'username', headerName: 'Username', sortable: true, filter: true },
        { field: 'email', headerName: 'Email', sortable: true, filter: true },
        {
            headerName: 'Name',
            valueGetter: (params) => `${params.data?.first_name || ''} ${params.data?.last_name || ''}`.trim(),
            sortable: true,
            filter: true,
        },
        {
            field: 'is_active',
            headerName: 'Active',
            valueGetter: (params) => params.data?.is_active ? 'Yes' : 'No',
            sortable: true,
            filter: true,
        },
        {
            field: 'is_staff',
            headerName: 'Staff',
            valueGetter: (params) => params.data?.is_staff ? 'Yes' : 'No',
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
                    <span>Users</span>
                    <Button variant="primary" size="sm" onClick={() => navigate(`${ROUTES.USERS}/add`)}>
                        Add User
                    </Button>
                </div>
            </div>
            <div style={{ height: '600px', width: '100%' }}>
                <DataTable<User>
                    columnDefs={columnDefs}
                    data={users}
                    isLoading={isLoading}
                    loadData={loadData}
                    noRowsMessage="No users found."
                />
            </div>
        </div>
    );
};

export default UserList;
