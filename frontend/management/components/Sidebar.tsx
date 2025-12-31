import { useState, useEffect } from 'react';
import { Nav, Button } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { SIDEBAR_WIDTH, NAVBAR_HEIGHT, COLORS, MENU_ITEMS, TRANSITION_DURATION } from '../constants/ui';
import type { SidebarProps } from '../types';

const Sidebar = ({ onToggle }: SidebarProps) => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const location = useLocation();
    const { isAuthenticated } = useAuth();

    useEffect(() => {
        if (onToggle) {
            onToggle(isCollapsed);
        }
    }, [isCollapsed, onToggle]);

    if (!isAuthenticated) {
        return null;
    }

    const sidebarStyle = {
        position: 'fixed' as const,
        left: 0,
        top: NAVBAR_HEIGHT,
        height: `calc(100vh - ${NAVBAR_HEIGHT})`,
        width: isCollapsed ? SIDEBAR_WIDTH.COLLAPSED : SIDEBAR_WIDTH.EXPANDED,
        backgroundColor: COLORS.LIGHT,
        borderRight: `1px solid ${COLORS.BORDER}`,
        transition: `width ${TRANSITION_DURATION.NORMAL} ease`,
        zIndex: 1000,
        overflow: 'hidden' as const,
    };

    return (
        <div style={sidebarStyle}>
            <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
                {!isCollapsed && (
                    <h6 className="mb-0 fw-bold">Quick Actions</h6>
                )}
                <Button
                    variant="link"
                    size="sm"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="p-1 text-muted"
                    style={{ minWidth: 'auto' }}
                    aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    {isCollapsed ? '→' : '←'}
                </Button>
            </div>
            <Nav className="flex-column p-2">
                {MENU_ITEMS.map((item) => {
                    const isActive = location.pathname.startsWith(item.path);
                    const linkClasses = `d-flex align-items-center gap-2 mb-1 rounded text-decoration-none ${
                        isActive ? 'bg-primary text-white' : 'text-dark'
                    }`;
                    
                    return (
                        <Nav.Link
                            key={item.path}
                            as={Link}
                            to={item.path}
                            className={linkClasses}
                            style={{
                                padding: '0.75rem 1rem',
                                transition: `all ${TRANSITION_DURATION.FAST} ease`,
                            }}
                            onMouseEnter={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.backgroundColor = COLORS.HOVER_BG;
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.backgroundColor = 'transparent';
                                }
                            }}
                        >
                            <span className={`fs-5 ${isActive ? 'text-white' : 'text-dark'}`} style={{ minWidth: '24px', textAlign: 'center' }}>
                                {item.icon}
                            </span>
                            {!isCollapsed && (
                                <span className={isActive ? 'text-white' : 'text-dark'}>
                                    {item.label}
                                </span>
                            )}
                        </Nav.Link>
                    );
                })}
            </Nav>
        </div>
    );
};

export default Sidebar;

