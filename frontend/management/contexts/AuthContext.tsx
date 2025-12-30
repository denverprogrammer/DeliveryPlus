import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getDashboard } from '../../shared/services/api';
import type { User } from '../../shared/types/api';

interface AuthContextType {
    isAuthenticated: boolean;
    user: User | null;
    setUser: (user: User | null) => void;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const checkAuth = async () => {
        try {
            await getDashboard();
            // If successful, user is authenticated
            setIsAuthenticated(true);
        } catch (error) {
            // Not authenticated
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const handleSetUser = (newUser: User | null) => {
        setUser(newUser);
        if (newUser) {
            setIsAuthenticated(true);
        }
    };

    const handleLogout = async () => {
        try {
            const { logout: logoutApi } = await import('../../shared/services/api');
            await logoutApi();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    const value: AuthContextType = {
        isAuthenticated,
        user,
        setUser: handleSetUser,
        logout: handleLogout,
        checkAuth,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

