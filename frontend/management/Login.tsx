import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { login } from '../shared/services/api';
import { useAuth } from './contexts/AuthContext';
import { isNonEmptyArray } from './utils/typeGuards';

interface LoginFormData {
    username: string;
    password: string;
}

const Login = () => {
    const navigate = useNavigate();
    const { setUser, checkAuth } = useAuth();
    const [formData, setFormData] = useState<LoginFormData>({
        username: '',
        password: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const response = await login(formData.username, formData.password);
            // Check if login was successful
            if (response.success) {
                // Set user in auth context
                setUser(response.user);
                // Re-check auth state
                await checkAuth();
                // Redirect to dashboard
                navigate('/dashboard');
            } else {
                setError('Login failed. Please check your credentials.');
            }
        } catch (err) {
            // Handle error response
            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { data?: { errors?: Record<string, string[]> } } };
                if (axiosError.response?.data?.errors) {
                    const errors = axiosError.response.data.errors;
                    // Get first error message
                    const firstError = Object.values(errors)[0];
                    if (Array.isArray(firstError) && isNonEmptyArray(firstError)) {
                        setError(firstError[0] as string);
                    } else {
                        setError('Login failed. Please check your credentials.');
                    }
                } else {
                    setError('Login failed. Please check your credentials.');
                }
            } else {
                setError(err instanceof Error ? err.message : 'Login failed');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="row justify-content-center mt-5">
            <div className="col-md-6">
                <Card>
                    <Card.Header>
                        <h2 className="mb-0">Login</h2>
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
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Password</Form.Label>
                                <Form.Control
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>

                            {error && (
                                <Alert variant="danger" className="mb-3">
                                    {error}
                                </Alert>
                            )}

                            <div className="d-flex gap-2">
                                <Button 
                                    type="submit" 
                                    variant="primary" 
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Logging in...' : 'Login'}
                                </Button>
                                <Button 
                                    type="button" 
                                    variant="secondary" 
                                    onClick={() => navigate('/signup')}
                                >
                                    Sign Up
                                </Button>
                            </div>
                        </Form>
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
};

export default Login; 