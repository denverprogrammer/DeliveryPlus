import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import { SIDEBAR_WIDTH, TRANSITION_DURATION } from '../constants/ui';
import { useNavigator } from '../utils/routes';
import type { LayoutProps } from '../types';

const Layout = ({ children }: LayoutProps) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const location = useLocation();
    const { isAuthenticated } = useAuth();
    const navigator = useNavigator();

    // Check if we should show sidebar (not on auth pages)
    const showSidebar = isAuthenticated && 
        !location.pathname.startsWith(navigator.getLoginUrl()) && 
        !location.pathname.startsWith(navigator.getSignupUrl());

    const containerStyle = {
        marginLeft: showSidebar ? (sidebarCollapsed ? SIDEBAR_WIDTH.COLLAPSED : SIDEBAR_WIDTH.EXPANDED) : '0',
        transition: `margin-left ${TRANSITION_DURATION.NORMAL} ease`,
        maxWidth: showSidebar ? `calc(100% - ${SIDEBAR_WIDTH.EXPANDED})` : '100%',
    };

    return (
        <>
            {showSidebar && <Sidebar onToggle={(collapsed) => setSidebarCollapsed(collapsed)} />}
            <Container className="mt-4" style={containerStyle}>
                {children}
            </Container>
        </>
    );
};

export default Layout;

