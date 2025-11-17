import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// Components
import Navigation from '../shared/components/Navigation';
import Home from '../shared/pages/Home';
import TrackingPage from '../shared/pages/TrackingPage';
import InterceptPage from '../shared/pages/InterceptPage';

function DeliveryApp() {
    return (
        <Router>
            <div className="App">
                <Navigation />
                <Container className="mt-4">
                    <Routes>
                        {/* Public/Delivery Routes Only */}
                        <Route path="/tracking" element={<TrackingPage />} />
                        <Route path="/notification/:token" element={<InterceptPage />} />
                        <Route path="/" element={<Home />} />
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default DeliveryApp; 