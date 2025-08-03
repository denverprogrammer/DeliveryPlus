import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// Components
import Navigation from '../shared/components/Navigation';
import Login from './Login';
import Dashboard from './Dashboard';
import AgentList from './AgentList';
import AgentForm from './AgentForm';
import CompanyEdit from './CompanyEdit';

function ManagementApp() {
    return (
        <Router>
            <div className="App">
                <Navigation />
                <Container className="mt-4">
                    <Routes>
                        {/* Management Routes Only */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/agents" element={<AgentList />} />
                        <Route path="/agents/add" element={<AgentForm />} />
                        <Route path="/agents/:id/edit" element={<AgentForm />} />
                        <Route path="/company/edit" element={<CompanyEdit />} />
                        <Route path="/" element={<Dashboard />} />
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default ManagementApp; 