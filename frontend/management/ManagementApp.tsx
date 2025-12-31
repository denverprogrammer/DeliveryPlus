import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootswatch/dist/sandstone/bootstrap.min.css';

// Components
import Navigation from './components/Navigation';
import Breadcrumbs from './components/Breadcrumbs';
import Layout from './components/Layout';
import Login from './Login';
import Signup from './Signup';
import Dashboard from './Dashboard';
import CompanyEdit from './CompanyEdit';
import UserList from './UserList';
import UserForm from './UserForm';
import CampaignList from './CampaignList';
import CampaignForm from './CampaignForm';
import CampaignDetail from './CampaignDetail';
import AllTrackingList from './AllTrackingList';
import TrackingForm from './TrackingForm';
import TrackingDetail from './TrackingDetail';
import { AuthProvider } from './contexts/AuthContext';

function ManagementApp() {
    return (
        <AuthProvider>
            <Router>
                <div className="App">
                    <Navigation />
                    <Layout>
                        <Breadcrumbs />
                        <Routes>
                        {/* Authentication */}
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/login" element={<Login />} />
                        {/* Dashboard */}
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/" element={<Dashboard />} />
                        {/* Company */}
                        <Route path="/company/edit" element={<CompanyEdit />} />
                        {/* Users */}
                        <Route path="/users" element={<UserList />} />
                        <Route path="/users/add" element={<UserForm />} />
                        <Route path="/users/:id/edit" element={<UserForm />} />
                        {/* Campaigns */}
                        <Route path="/campaigns" element={<CampaignList />} />
                        <Route path="/campaigns/add" element={<CampaignForm />} />
                        <Route path="/campaigns/:id" element={<CampaignDetail />} />
                        <Route path="/campaigns/:id/edit" element={<CampaignForm />} />
                        {/* Tracking (top-level) */}
                        <Route path="/tracking" element={<AllTrackingList />} />
                        <Route path="/tracking/add" element={<TrackingForm />} />
                        <Route path="/tracking/:id" element={<TrackingDetail />} />
                        <Route path="/tracking/:id/edit" element={<TrackingForm />} />
                        </Routes>
                    </Layout>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default ManagementApp; 