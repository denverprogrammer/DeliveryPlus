import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import { SIDEBAR_WIDTH, ROUTES, TRANSITION_DURATION } from '../constants/ui';
import type { LayoutProps } from '../types';

const Layout = ({ children }: LayoutProps) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const location = useLocation();
    const { isAuthenticated } = useAuth();

    // Check if we should show sidebar (not on auth pages)
    const showSidebar = isAuthenticated && 
        !location.pathname.startsWith(ROUTES.LOGIN) && 
        !location.pathname.startsWith(ROUTES.SIGNUP);

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

