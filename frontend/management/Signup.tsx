import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import { signup } from '../shared/services/api';
import { useAuth } from './contexts/AuthContext';

const Signup = () => {
    const navigate = useNavigate();
    const { checkAuth } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password1: '',
        password2: '',
        company_name: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [errors, setErrors] = useState<Record<string, string[]>>({});

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
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
            const response = await signup({
                username: formData.username,
                email: formData.email,
                password1: formData.password1,
                password2: formData.password2,
                company_name: formData.company_name,
            });
            if (response.success) {
                // Re-check auth state after signup
                await checkAuth();
                navigate('/dashboard');
            }
        } catch (err: any) {
            if (err.response?.data?.errors) {
                setErrors(err.response.data.errors);
            } else {
                setError(err instanceof Error ? err.message : 'Signup failed');
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
                        <h2 className="mb-0">Sign Up</h2>
                    </Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Company Name</Form.Label>
                                <Form.Control
                                    type="text"
                                    name="company_name"
                                    value={formData.company_name}
                                    onChange={handleChange}
                                    required
                                    isInvalid={!!errors.company_name}
                                />
                                {errors.company_name && (
                                    <Form.Control.Feedback type="invalid">
                                        {errors.company_name[0]}
                                    </Form.Control.Feedback>
                                )}
                            </Form.Group>

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
                                <Form.Label>Password</Form.Label>
                                <Form.Control
                                    type="password"
                                    name="password1"
                                    value={formData.password1}
                                    onChange={handleChange}
                                    required
                                    isInvalid={!!errors.password1}
                                />
                                {errors.password1 && (
                                    <Form.Control.Feedback type="invalid">
                                        {errors.password1[0]}
                                    </Form.Control.Feedback>
                                )}
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Confirm Password</Form.Label>
                                <Form.Control
                                    type="password"
                                    name="password2"
                                    value={formData.password2}
                                    onChange={handleChange}
                                    required
                                    isInvalid={!!errors.password2}
                                />
                                {errors.password2 && (
                                    <Form.Control.Feedback type="invalid">
                                        {errors.password2[0]}
                                    </Form.Control.Feedback>
                                )}
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
                                    {isLoading ? 'Signing up...' : 'Sign Up'}
                                </Button>
                                <Button 
                                    type="button" 
                                    variant="secondary" 
                                    onClick={() => navigate('/login')}
                                >
                                    Back to Login
                                </Button>
                            </div>
                        </Form>
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
};

export default Signup;
