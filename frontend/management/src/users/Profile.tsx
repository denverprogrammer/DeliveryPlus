import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Alert } from 'react-bootstrap';
import { getCurrentUser, updateUser } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { ROUTES } from '../constants/ui';
import type { UserUpdatePayload } from '../types/api';

interface ProfileFormData {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
}

interface PasswordFormData {
    current_password: string;
    new_password: string;
    confirm_password: string;
}

const Profile = () => {
    const navigate = useNavigate();
    const { user: currentUser, setUser } = useAuth();
    const { theme, colorScheme, iconSet, setTheme, setColorScheme, setIconSet } = useTheme();
    const [profileData, setProfileData] = useState<ProfileFormData>({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
    });
    const [passwordData, setPasswordData] = useState<PasswordFormData>({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingPassword, setIsLoadingPassword] = useState(false);
    const [isLoadingData, setIsLoadingData] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [passwordError, setPasswordError] = useState<string | null>(null);
    const [errors, setErrors] = useState<Record<string, string[]>>({});
    const [passwordErrors, setPasswordErrors] = useState<Record<string, string[]>>({});

    useEffect(() => {
        loadUser();
    }, []);

    const loadUser = async () => {
        try {
            setIsLoadingData(true);
            setError(null);
            const user = await getCurrentUser();
            setProfileData({
                username: user.username || '',
                email: user.email || '',
                first_name: user.first_name || '',
                last_name: user.last_name || '',
            });
            // Update the user in auth context
            setUser(user);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load user data');
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setProfileData(prev => ({
            ...prev,
            [name]: value,
        }));
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({
            ...prev,
            [name]: value,
        }));
        // Clear error for this field
        if (passwordErrors[name]) {
            setPasswordErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const handleProfileSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setErrors({});

        try {
            setIsLoading(true);
            const payload: UserUpdatePayload = {
                username: profileData.username,
                email: profileData.email,
                first_name: profileData.first_name || undefined,
                last_name: profileData.last_name || undefined,
            };

            // Get current user ID - fetch if not in context
            let userId = currentUser?.id;
            if (!userId) {
                const currentUserData = await getCurrentUser();
                userId = currentUserData.id;
            }

            const updatedUser = await updateUser(userId, payload);
            setUser(updatedUser);
            
            navigate(ROUTES.DASHBOARD);
        } catch (err: unknown) {
            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { data?: { errors?: Record<string, string[]> } } };
                if (axiosError.response?.data?.errors) {
                    setErrors(axiosError.response.data.errors);
                } else {
                    setError('Failed to update profile');
                }
            } else {
                setError(err instanceof Error ? err.message : 'Failed to update profile');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setPasswordError(null);
        setPasswordErrors({});

        // Validate passwords match
        if (passwordData.new_password !== passwordData.confirm_password) {
            setPasswordErrors({ new_password: ['Passwords do not match'] });
            return;
        }

        // Validate all fields are provided
        if (!passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password) {
            setPasswordErrors({ new_password: ['All password fields are required'] });
            return;
        }

        try {
            setIsLoadingPassword(true);
            const payload: UserUpdatePayload = {
                password: passwordData.new_password,
                current_password: passwordData.current_password,
            };

            // Get current user ID - fetch if not in context
            let userId = currentUser?.id;
            if (!userId) {
                const currentUserData = await getCurrentUser();
                userId = currentUserData.id;
            }

            await updateUser(userId, payload);
            
            // Clear password form on success
            setPasswordData({
                current_password: '',
                new_password: '',
                confirm_password: '',
            });
            
            // Show success message or navigate
            setPasswordError(null);
        } catch (err: unknown) {
            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { data?: { errors?: Record<string, string[]> } } };
                if (axiosError.response?.data?.errors) {
                    setPasswordErrors(axiosError.response.data.errors);
                } else {
                    setPasswordError('Failed to update password');
                }
            } else {
                setPasswordError(err instanceof Error ? err.message : 'Failed to update password');
            }
        } finally {
            setIsLoadingPassword(false);
        }
    };

    if (isLoadingData) {
        return <div>Loading...</div>;
    }

    if (!currentUser) {
        return <Alert variant="danger">You must be logged in to view your profile.</Alert>;
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>My Profile</h3>
                <Button variant="secondary" onClick={() => navigate(ROUTES.DASHBOARD)}>
                    Back to Dashboard
                </Button>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            {/* Profile Information Form */}
            <div className="mb-5">
                <h4 className="mb-3">Profile Information</h4>
                <Form onSubmit={handleProfileSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Username</Form.Label>
                        <Form.Control
                            type="text"
                            name="username"
                            value={profileData.username}
                            onChange={handleProfileChange}
                            isInvalid={!!errors.username}
                            required
                        />
                        {errors.username && (
                            <Form.Control.Feedback type="invalid">
                                {errors.username.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Email</Form.Label>
                        <Form.Control
                            type="email"
                            name="email"
                            value={profileData.email}
                            onChange={handleProfileChange}
                            isInvalid={!!errors.email}
                            required
                        />
                        {errors.email && (
                            <Form.Control.Feedback type="invalid">
                                {errors.email.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>First Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="first_name"
                            value={profileData.first_name}
                            onChange={handleProfileChange}
                            isInvalid={!!errors.first_name}
                        />
                        {errors.first_name && (
                            <Form.Control.Feedback type="invalid">
                                {errors.first_name.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Last Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="last_name"
                            value={profileData.last_name}
                            onChange={handleProfileChange}
                            isInvalid={!!errors.last_name}
                        />
                        {errors.last_name && (
                            <Form.Control.Feedback type="invalid">
                                {errors.last_name.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <div className="d-flex gap-2">
                        <Button variant="primary" type="submit" disabled={isLoading}>
                            {isLoading ? 'Saving...' : 'Save Profile'}
                        </Button>
                        <Button variant="secondary" onClick={() => navigate(ROUTES.DASHBOARD)}>
                            Cancel
                        </Button>
                    </div>
                </Form>
            </div>

            {/* Password Change Form */}
            <div>
                <h4 className="mb-3">Change Password</h4>
                {passwordError && <Alert variant="danger" className="mb-3">{passwordError}</Alert>}
                <Form onSubmit={handlePasswordSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Current Password</Form.Label>
                        <Form.Control
                            type="password"
                            name="current_password"
                            value={passwordData.current_password}
                            onChange={handlePasswordChange}
                            isInvalid={!!passwordErrors.current_password}
                            required
                        />
                        {passwordErrors.current_password && (
                            <Form.Control.Feedback type="invalid">
                                {passwordErrors.current_password.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>New Password</Form.Label>
                        <Form.Control
                            type="password"
                            name="new_password"
                            value={passwordData.new_password}
                            onChange={handlePasswordChange}
                            isInvalid={!!passwordErrors.new_password}
                            required
                        />
                        {passwordErrors.new_password && (
                            <Form.Control.Feedback type="invalid">
                                {passwordErrors.new_password.join(', ')}
                            </Form.Control.Feedback>
                        )}
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Confirm New Password</Form.Label>
                        <Form.Control
                            type="password"
                            name="confirm_password"
                            value={passwordData.confirm_password}
                            onChange={handlePasswordChange}
                            isInvalid={!!passwordErrors.new_password}
                            required
                        />
                    </Form.Group>

                    <div className="d-flex gap-2">
                        <Button variant="primary" type="submit" disabled={isLoadingPassword}>
                            {isLoadingPassword ? 'Changing Password...' : 'Change Password'}
                        </Button>
                    </div>
                </Form>
            </div>

            {/* Theme Preferences */}
            <div className="mt-5">
                <h4 className="mb-3">Table Theme Preferences</h4>
                <div className="d-flex gap-2 mb-3 flex-wrap">
                    <div>
                        <Form.Label>Theme</Form.Label>
                        <Form.Select
                            value={theme}
                            onChange={(e) => setTheme(e.target.value)}
                            style={{ width: '200px' }}
                        >
                            <option value="quartz">Quartz</option>
                            <option value="balham">Balham</option>
                            <option value="alpine">Alpine</option>
                            <option value="material">Material</option>
                        </Form.Select>
                    </div>
                    <div>
                        <Form.Label>Color Scheme</Form.Label>
                        <Form.Select
                            value={colorScheme}
                            onChange={(e) => setColorScheme(e.target.value)}
                            style={{ width: '180px' }}
                        >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="variable">Variable</option>
                            <option value="light-warm">Light Warm</option>
                            <option value="light-cold">Light Cold</option>
                            <option value="dark-warm">Dark Warm</option>
                            <option value="dark-blue">Dark Blue</option>
                        </Form.Select>
                    </div>
                    <div>
                        <Form.Label>Icon Set</Form.Label>
                        <Form.Select
                            value={iconSet}
                            onChange={(e) => setIconSet(e.target.value)}
                            style={{ width: '180px' }}
                        >
                            <option value="quartz">Quartz</option>
                            <option value="material">Material</option>
                            <option value="alpine">Alpine</option>
                            <option value="quartz-bold">Quartz Bold</option>
                            <option value="quartz-light">Quartz Light</option>
                            <option value="quartz-regular">Quartz Regular</option>
                        </Form.Select>
                    </div>
                </div>
                <p className="text-muted small">These preferences are saved automatically and will be applied to all tables in the application.</p>
            </div>
        </div>
    );
};

export default Profile;

