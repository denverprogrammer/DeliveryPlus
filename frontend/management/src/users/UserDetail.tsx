import { useEffect, useState } from 'react';
import { Table, Button, Alert } from 'react-bootstrap';
import { getUser } from '../services/api';
import { useParsedParam } from '../utils/params';
import { TABLE_CAPTION_STYLE, NOT_AVAILABLE } from '../constants/ui';
import type { User } from '../types/api';
import { useNavigator } from '../utils/routes';

const UserDetail = () => {
    const navigator = useNavigator();
    const [userId] = useParsedParam('id');
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (userId !== null) {
            loadUser();
        } else {
            setError('Invalid user ID');
            setIsLoading(false);
        }
    }, [userId]);

    const loadUser = async () => {
        if (userId === null) {
            return;
        }
        try {
            setIsLoading(true);
            setError(null);
            const userData = await getUser(userId);
            setUser(userData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load user');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error || !user) {
        return <Alert variant="danger">{error || 'User not found'}</Alert>;
    }

    const companyName = typeof user.company === 'object' && user.company !== null
        ? user.company.name
        : NOT_AVAILABLE;

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>User Details</h3>
                <div className="d-flex gap-2">
                    <Button variant="primary" onClick={() => navigator.sendToEditUser(user.id)}>
                        Edit
                    </Button>
                    <Button variant="secondary" onClick={() => navigator.sendToUsers()}>
                        Back to List
                    </Button>
                </div>
            </div>

            <div className="fw-bold mb-2" style={TABLE_CAPTION_STYLE}>
                User Information
            </div>
            <Table striped bordered hover>
                <tbody>
                    <tr>
                        <td><strong>ID</strong></td>
                        <td>{user.id}</td>
                    </tr>
                    <tr>
                        <td><strong>Username</strong></td>
                        <td>{user.username || NOT_AVAILABLE}</td>
                    </tr>
                    <tr>
                        <td><strong>Email</strong></td>
                        <td>{user.email || NOT_AVAILABLE}</td>
                    </tr>
                    <tr>
                        <td><strong>First Name</strong></td>
                        <td>{user.first_name || NOT_AVAILABLE}</td>
                    </tr>
                    <tr>
                        <td><strong>Last Name</strong></td>
                        <td>{user.last_name || NOT_AVAILABLE}</td>
                    </tr>
                    <tr>
                        <td><strong>Full Name</strong></td>
                        <td>{`${user.first_name || ''} ${user.last_name || ''}`.trim() || NOT_AVAILABLE}</td>
                    </tr>
                    <tr>
                        <td><strong>Active</strong></td>
                        <td>{user.is_active ? 'Yes' : 'No'}</td>
                    </tr>
                    <tr>
                        <td><strong>Staff</strong></td>
                        <td>{user.is_staff ? 'Yes' : 'No'}</td>
                    </tr>
                    <tr>
                        <td><strong>Company</strong></td>
                        <td>{companyName}</td>
                    </tr>
                </tbody>
            </Table>
        </div>
    );
};

export default UserDetail;

