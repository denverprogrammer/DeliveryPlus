import { useState, useCallback } from 'react';
import { GridApi } from 'ag-grid-community';
import { Button, Alert } from 'react-bootstrap';
import { getUsers, deleteUser } from '../services/api';
import { TABLE_CAPTION_STYLE } from '../constants/ui';
import type { User } from '../types/api';
import DataTable from '../components/DataTable';
import type { PaginationParams } from '../types/api';
import { useNavigator } from '../utils/routes';
import { useColumnDefs } from '../hooks/useColumnDefs';

const UserList = () => {
    const navigator = useNavigator();
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

    const handleView = useCallback((user: User) => {
        navigator.sendToUser(user.id);
    }, [navigator]);

    const handleEdit = useCallback((user: User) => {
        navigator.sendToEditUser(user.id);
    }, [navigator]);

    const handleDelete = useCallback(async (user: User) => {
        if (!window.confirm('Are you sure you want to delete this user?')) {
            return;
        }
        try {
            await deleteUser(user.id);
            const response = await getUsers();
            setUsers(response.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete user');
            throw err;
        }
    }, []);

    const columnDefs = useColumnDefs<User>('userList', { view: handleView, edit: handleEdit, delete: handleDelete });

    return (
        <div>
            {error && <Alert variant="danger" className="mb-3">{error}</Alert>}
            <div className="p-0 fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                <div className="d-flex justify-content-between align-items-center">
                    <span>Users</span>
                    <Button variant="primary" size="sm" onClick={() => navigator.sendToAddUser()}>
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
