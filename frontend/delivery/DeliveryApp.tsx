import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// Components
import Navigation from '../shared/components/Navigation';
import Home from '../shared/pages/Home';
import Tracking from '../shared/pages/Tracking';
import Redirect from '../shared/pages/Redirect';

function DeliveryApp() {
    return (
        <Router>
            <div className="App">
                <Navigation />
                <Container className="mt-4">
                    <Routes>
                        {/* Public/Delivery Routes Only */}
                        <Route path="/" element={<Home />} />
                        <Route path="/tracking" element={<Tracking />} />
                        <Route path="/tracking/:token" element={<Tracking />} />
                        <Route path="/redirects" element={<Redirect />} />
                        <Route path="/redirects/:token" element={<Redirect />} />
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default DeliveryApp; 