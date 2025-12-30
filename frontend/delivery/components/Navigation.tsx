import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
    const location = useLocation();

    return (
        <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
            <Container fluid>
                <Navbar.Brand as={Link} to="/">
                    packageparcels
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link 
                            as={Link} 
                            to="/tracking" 
                            active={location.pathname.startsWith('/tracking') || 
                                   location.pathname.startsWith('/redirects') || 
                                   location.pathname.startsWith('/services')}
                        >
                            Tracking
                        </Nav.Link>
                    </Nav>
                    
                    <Nav>
                        <Nav.Link as={Link} to="/login">Management</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;

