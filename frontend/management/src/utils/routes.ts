import { useNavigate } from 'react-router-dom';

/**
 * React hook that provides navigation methods with navigate already bound.
 * Usage: const navigator = useNavigator(); navigator.sendToUsers(); navigator.getEditCompanyUrl(123);
 */
export const useNavigator = () => {
    const navigate = useNavigate();

    // URL getters
    const getDashboardUrl = () => '/dashboard';
    const getEditCompanyUrl = () => '/company/edit';
    const getProfileUrl = () => '/profile';
    const getLoginUrl = () => '/login';
    const getSignupUrl = () => '/signup';
    const getUsersUrl = () => '/users';
    const getAddUserUrl = () => '/users/add';
    const getUserUrl = (id: number) => `/users/${id}`;
    const getEditUserUrl = (id: number) => `/users/${id}/edit`;
    const getCampaignsUrl = () => '/campaigns';
    const getAddCampaignUrl = () => '/campaigns/add';
    const getCampaignUrl = (id: number) => `/campaigns/${id}`;
    const getEditCampaignUrl = (id: number) => `/campaigns/${id}/edit`;
    const getTrackingUrl = () => '/tracking';
    const getAddTrackingUrl = () => '/tracking/add';
    const getTrackingUrlById = (id: number) => `/tracking/${id}`;
    const getEditTrackingUrl = (id: number) => `/tracking/${id}/edit`;
    const getRecipientsUrl = () => '/recipients';
    const getAddRecipientUrl = () => '/recipients/add';
    const getEditRecipientUrl = (id: number) => `/recipients/${id}/edit`;

    return {
        // Dashboard
        getDashboardUrl,
        sendToDashboard: () => navigate(getDashboardUrl()),

        // Company
        getEditCompanyUrl,
        sendToEditCompany: () => navigate(getEditCompanyUrl()),

        // Profile
        getProfileUrl,
        sendToProfile: () => navigate(getProfileUrl()),

        // Login
        getLoginUrl,
        sendToLogin: () => navigate(getLoginUrl()),

        // Signup
        getSignupUrl,
        sendToSignup: () => navigate(getSignupUrl()),

        // Users
        getUsersUrl,
        sendToUsers: () => navigate(getUsersUrl()),

        getAddUserUrl,
        sendToAddUser: () => navigate(getAddUserUrl()),

        getUserUrl,
        sendToUser: (id: number) => navigate(getUserUrl(id)),

        getEditUserUrl,
        sendToEditUser: (id: number) => navigate(getEditUserUrl(id)),

        // Campaigns
        getCampaignsUrl,
        sendToCampaigns: () => navigate(getCampaignsUrl()),

        getAddCampaignUrl,
        sendToAddCampaign: () => navigate(getAddCampaignUrl()),

        getCampaignUrl,
        sendToCampaign: (id: number) => navigate(getCampaignUrl(id)),

        getEditCampaignUrl,
        sendToEditCampaign: (id: number) => navigate(getEditCampaignUrl(id)),

        // Tracking
        getTrackingUrl,
        sendToTracking: () => navigate(getTrackingUrl()),

        getAddTrackingUrl,
        sendToAddTracking: () => navigate(getAddTrackingUrl()),

        getTrackingUrlById,
        sendToTrackingById: (id: number) => navigate(getTrackingUrlById(id)),

        getEditTrackingUrl,
        sendToEditTracking: (id: number) => navigate(getEditTrackingUrl(id)),

        // Recipients
        getRecipientsUrl,
        sendToRecipients: () => navigate(getRecipientsUrl()),

        getAddRecipientUrl,
        sendToAddRecipient: () => navigate(getAddRecipientUrl()),

        getEditRecipientUrl,
        sendToEditRecipient: (id: number) => navigate(getEditRecipientUrl(id)),
    };
};
