import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import 'bootswatch/dist/sandstone/bootstrap.min.css';
import 'ag-grid-community/styles/ag-grid.css';
// Import all themes for testing
import 'ag-grid-community/styles/ag-theme-quartz.css';
import 'ag-grid-community/styles/ag-theme-balham.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import 'ag-grid-community/styles/ag-theme-material.css';

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule]);

// Components
import Navigation from './components/Navigation';
import Breadcrumbs from './components/Breadcrumbs';
import Layout from './components/Layout';
import Login from './Login';
import Signup from './Signup';
import Dashboard from './Dashboard';
import CompanyEdit from './CompanyEdit';
import UserList from './users/UserList';
import UserForm from './users/UserForm';
import CampaignList from './campaigns/CampaignList';
import CampaignForm from './campaigns/CampaignForm';
import CampaignDetail from './campaigns/CampaignDetail';
import TrackingList from './tracking/TrackingList';
import TrackingForm from './tracking/TrackingForm';
import TrackingDetail from './tracking/TrackingDetail';
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
                        <Route path="/tracking" element={<TrackingList />} />
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