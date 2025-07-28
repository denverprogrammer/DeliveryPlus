import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Components
import Navigation from './components/Navigation';
import Home from './pages/Home';
import Tracking from './pages/Tracking';
import Redirect from './pages/Redirect';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AgentList from './pages/AgentList';
import AgentForm from './pages/AgentForm';
import CompanyEdit from './pages/CompanyEdit';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tracking" element={<Tracking />} />
            <Route path="/tracking/:token" element={<Tracking />} />
            <Route path="/redirects" element={<Redirect />} />
            <Route path="/redirects/:token" element={<Redirect />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/agents" element={<AgentList />} />
            <Route path="/agents/add" element={<AgentForm />} />
            <Route path="/agents/:id/edit" element={<AgentForm />} />
            <Route path="/company/edit" element={<CompanyEdit />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;
