import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated, logout } = useAuth();
    
    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };
    
    // Determine if we're in the management section
    // If authenticated and on root path, assume management site
    const isManagementSite = (isAuthenticated && location.pathname === '/') ||
                             location.pathname.startsWith('/mgmt') || 
                             location.pathname.startsWith('/signup') ||
                             location.pathname.startsWith('/login') ||
                             location.pathname.startsWith('/dashboard') ||
                             location.pathname.startsWith('/users') ||
                             location.pathname.startsWith('/campaigns') ||
                             location.pathname.startsWith('/tracking') ||
                             location.pathname.startsWith('/company');

    return (
        <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
            <Container fluid>
                <Navbar.Brand as={Link} to="/dashboard">
                    packageparcels
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        {isManagementSite && isAuthenticated && (
                            <>
                                <Nav.Link 
                                    as={Link} 
                                    to="/dashboard" 
                                    active={location.pathname === '/dashboard' || location.pathname === '/'}
                                >
                                    Dashboard
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/users" 
                                    active={location.pathname.startsWith('/users')}
                                >
                                    Users
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/campaigns" 
                                    active={location.pathname.startsWith('/campaigns')}
                                >
                                    Campaigns
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/tracking" 
                                    active={location.pathname.startsWith('/tracking')}
                                >
                                    Tracking
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/company/edit" 
                                    active={location.pathname === '/company/edit'}
                                >
                                    Company
                                </Nav.Link>
                            </>
                        )}
                    </Nav>
                    
                    <Nav>
                        {isManagementSite && !isAuthenticated && (
                            <>
                                <Nav.Link as={Link} to="/signup">Sign Up</Nav.Link>
                                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                            </>
                        )}
                        {isManagementSite && isAuthenticated && (
                            <Nav.Link as="a" href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                                Logout
                            </Nav.Link>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;

