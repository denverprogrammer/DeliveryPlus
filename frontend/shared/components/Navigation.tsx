import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
    const location = useLocation();
    
    // Mock authentication state - in real app, this would come from context/state
    const isAuthenticated = false; // This will be replaced with actual auth state
    
    // Determine if we're in the management section
    const isManagementSite = location.pathname.startsWith('/mgmt');
    
    // Determine if we're in the delivery section
    const isDeliverySite = location.pathname.startsWith('/tracking') || 
                          location.pathname.startsWith('/redirects') ||
                          location.pathname.startsWith('/services') ||
                          location.pathname === '/';

    return (
        <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
            <Container fluid>
                <Navbar.Brand as={Link} to={isManagementSite ? "/mgmt/dashboard" : "/"}>
                    packageparcels
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        {isDeliverySite && (
                            <>
                                <Nav.Link 
                                    as={Link} 
                                    to="/tracking" 
                                    active={location.pathname.startsWith('/tracking') || 
                                           location.pathname.startsWith('/redirects') || 
                                           location.pathname.startsWith('/services')}
                                >
                                    Tracking
                                </Nav.Link>
                            </>
                        )}
                        
                        {isManagementSite && isAuthenticated && (
                            <>
                                <Nav.Link 
                                    as={Link} 
                                    to="/mgmt/dashboard" 
                                    active={location.pathname === '/mgmt/dashboard'}
                                >
                                    Dashboard
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/mgmt/agents" 
                                    active={location.pathname.startsWith('/mgmt/agents')}
                                >
                                    Agents
                                </Nav.Link>
                                <Nav.Link 
                                    as={Link} 
                                    to="/mgmt/company/edit" 
                                    active={location.pathname === '/mgmt/company/edit'}
                                >
                                    Company
                                </Nav.Link>
                            </>
                        )}
                    </Nav>
                    
                    <Nav>
                        {isManagementSite && !isAuthenticated && (
                            <Nav.Link as={Link} to="/mgmt/login">Login</Nav.Link>
                        )}
                        {isManagementSite && isAuthenticated && (
                            <Nav.Link as={Link} to="/mgmt/logout">Logout</Nav.Link>
                        )}
                        {isDeliverySite && (
                            <Nav.Link as={Link} to="/mgmt/login">Management</Nav.Link>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation; 