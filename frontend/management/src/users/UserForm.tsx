import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { getUser, createUser, updateUser } from '../services/api';
import { useParsedParam } from '../utils/params';
import type { UserCreatePayload, UserUpdatePayload } from '../types/api';

interface UserFormData {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    is_active: boolean;
    is_staff: boolean;
}

const UserForm = () => {
    const navigate = useNavigate();
    const [userId] = useParsedParam('id');
    const isEdit = userId !== null;
    const [formData, setFormData] = useState<UserFormData>({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_active: true,
        is_staff: false,
    });
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingData, setIsLoadingData] = useState(isEdit);
    const [error, setError] = useState<string | null>(null);
    const [errors, setErrors] = useState<Record<string, string[]>>({});

    useEffect(() => {
        if (isEdit && userId !== null) {
            loadUser();
        }
    }, [userId, isEdit]);

    const loadUser = async () => {
        if (userId === null) {
            return;
        }
        try {
            setIsLoadingData(true);
            const user = await getUser(userId);
            setFormData({
                username: user.username || '',
                email: user.email || '',
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                password: '',
                is_active: user.is_active ?? true,
                is_staff: user.is_staff ?? false,
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load user');
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: value,
        });
        if (errors[e.target.name]) {
            const newErrors = { ...errors };
            delete newErrors[e.target.name];
            setErrors(newErrors);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setErrors({});

        try {
            if (isEdit && userId !== null) {
                const data: UserUpdatePayload = {
                    username: formData.username,
                    email: formData.email,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                };
                await updateUser(userId, data);
            } else {
                const data: UserCreatePayload = {
                    username: formData.username,
                    email: formData.email,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    password: formData.password,
                    is_active: formData.is_active,
                    is_staff: formData.is_staff,
                };
                await createUser(data);
            }
            navigate('/users');
        } catch (err: any) {
            if (err.response?.data?.errors) {
                setErrors(err.response.data.errors);
            } else {
                setError(err instanceof Error ? err.message : 'Failed to save user');
            }
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoadingData) {
        return <div>Loading...</div>;
    }

    return (
        <Card>
            <Card.Header>
                <h3 className="mb-0">{isEdit ? 'Edit User' : 'Add User'}</h3>
            </Card.Header>
            <Card.Body>
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Username</Form.Label>
                        <Form.Control
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            isInvalid={!!errors.username}
                        />
                        {errors.username && (
                            <Form.Control.Feedback type="invalid">
                                {errors.username[0]}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Email</Form.Label>
                        <Form.Control
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            isInvalid={!!errors.email}
                        />
                        {errors.email && (
                            <Form.Control.Feedback type="invalid">
                                {errors.email[0]}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>First Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Last Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                        />
                    </Form.Group>

                    {!isEdit && (
                        <>
                            <Form.Group className="mb-3">
                                <Form.Label>Password</Form.Label>
                                <Form.Control
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    isInvalid={!!errors.password}
                                />
                                {errors.password && (
                                    <Form.Control.Feedback type="invalid">
                                        {errors.password[0]}
                                    </Form.Control.Feedback>
                                )}
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Check
                                    type="checkbox"
                                    name="is_active"
                                    label="Active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Check
                                    type="checkbox"
                                    name="is_staff"
                                    label="Staff"
                                    checked={formData.is_staff}
                                    onChange={handleChange}
                                />
                            </Form.Group>
                        </>
                    )}

                    {error && (
                        <Alert variant="danger" className="mb-3">
                            {error}
                        </Alert>
                    )}

                    <div className="d-flex gap-2">
                        <Button type="submit" variant="primary" disabled={isLoading}>
                            {isLoading ? 'Saving...' : 'Save'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => navigate('/users')}>
                            Cancel
                        </Button>
                    </div>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default UserForm;
