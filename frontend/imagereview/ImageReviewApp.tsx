import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import ImageReviewPage from './pages/ImageReviewPage';

function ImageReviewApp() {
    return (
        <Router>
            <div className="App">
                <Container className="mt-4">
                    <Routes>
                        <Route path="/" element={<ImageReviewPage />} />
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default ImageReviewApp;

