import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  
  // Mock authentication state - in real app, this would come from context/state
  const isAuthenticated = false; // This will be replaced with actual auth state

  return (
    <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
      <Container fluid>
        <Navbar.Brand as={Link} to="/">packageparcels</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link 
              as={Link} 
              to="/tracking" 
              active={location.pathname === '/tracking'}
            >
              Tracking
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/redirects" 
              active={location.pathname === '/redirects'}
            >
              Redirects
            </Nav.Link>
            {isAuthenticated && (
              <>
                <Nav.Link 
                  as={Link} 
                  to="/dashboard" 
                  active={location.pathname === '/dashboard'}
                >
                  Dashboard
                </Nav.Link>
                <Nav.Link 
                  as={Link} 
                  to="/agents" 
                  active={location.pathname === '/agents'}
                >
                  Agents
                </Nav.Link>
                <Nav.Link 
                  as={Link} 
                  to="/company/edit" 
                  active={location.pathname === '/company/edit'}
                >
                  Company
                </Nav.Link>
                <Nav.Link as={Link} to="/logout">Logout</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation; 