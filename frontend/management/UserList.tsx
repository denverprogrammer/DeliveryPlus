import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Alert, Card } from 'react-bootstrap';
import { getUsers, deleteUser } from '../shared/services/api';

interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
    is_staff: boolean;
}

const UserList = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState<User[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadUsers = async () => {
        try {
            setIsLoading(true);
            const response = await getUsers();
            setUsers(response || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load users');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this user?')) {
            return;
        }
        try {
            await deleteUser(id);
            loadUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete user');
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
                <h3 className="mb-0">Users</h3>
                <Button variant="primary" onClick={() => navigate('/users/add')}>
                    Add User
                </Button>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Name</th>
                            <th>Active</th>
                            <th>Staff</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id}>
                                <td>{user.username}</td>
                                <td>{user.email}</td>
                                <td>{user.first_name} {user.last_name}</td>
                                <td>{user.is_active ? 'Yes' : 'No'}</td>
                                <td>{user.is_staff ? 'Yes' : 'No'}</td>
                                <td>
                                    <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={() => navigate(`/users/${user.id}/edit`)}
                                        className="me-2"
                                    >
                                        Edit
                                    </Button>
                                    <Button
                                        variant="danger"
                                        size="sm"
                                        onClick={() => handleDelete(user.id)}
                                    >
                                        Delete
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Card.Body>
        </Card>
    );
};

export default UserList;
