import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '../constants/ui';

const Navigation = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated, logout, user } = useAuth();
    
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
                             location.pathname.startsWith('/company') ||
                             location.pathname.startsWith('/profile');

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
                            <Nav.Link 
                                as={Link} 
                                to="/dashboard" 
                                active={location.pathname === '/dashboard' || location.pathname === '/'}
                            >
                                Dashboard
                            </Nav.Link>
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
                            <>
                                <Nav.Link 
                                    as={Link} 
                                    to={ROUTES.PROFILE}
                                    active={location.pathname === ROUTES.PROFILE}
                                >
                                    Welcome {user?.username || 'User'}
                                </Nav.Link>
                                <Nav.Link as="a" href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                                    Logout
                                </Nav.Link>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;

