import axios from 'axios';
import { prepareTrackingHeader } from './trackingUtils';
import type {
    Company,
    User,
    UserCreatePayload,
    UserUpdatePayload,
    Recipient,
    Campaign,
    CampaignCreatePayload,
    CampaignUpdatePayload,
    Tracking,
    TrackingCreatePayload,
    TrackingUpdatePayload,
    CompanyUpdatePayload,
    LoginResponse,
    SignupResponse,
    SignupPayload,
    DashboardData,
    PaginatedResponse,
    RequestData,
    RequestDataDetail,
} from '../types/api';

// Configure axios defaults
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Required for session authentication
});

// Request interceptor to add auth token and CSRF token
api.interceptors.request.use(async (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    // Get CSRF token from cookies for session authentication
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        config.headers['X-CSRFToken'] = csrftoken;
    }
    return config;
});

// Helper function to get cookie value
function getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()?.split(';').shift() || null;
    }
    return null;
}

// Response interceptor to handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API functions
export const sendTrackingData = async (token: string): Promise<unknown> => {
    const headerValue = await prepareTrackingHeader();
    
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch(`/api/packages/track/`, {
        method: 'POST',
        body: JSON.stringify({
			method: 'POST',
			token: token,
		}),
        headers,
    });

    return response.json();
};

export const sendRedirectData = async (token: string, notifications?: string): Promise<unknown> => {
    const headerValue = await prepareTrackingHeader();
    
    const formData = new FormData();
    formData.append('http_method', 'POST');
    formData.append('token', token);
    if (notifications) {
        formData.append('notifications', notifications);
    }

    const headers: Record<string, string> = {
        'Content-Type': 'multipart/form-data',
    };

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch(`/api/packages/${token}/intercept/`, {
        method: 'POST',
        body: formData,
        headers,
    });

    return response.json();
};

// Auth functions
export const login = async (username: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/api/management/users/login/', { username, password });
    return response.data;
};

export const logout = async (): Promise<void> => {
    await api.post('/api/management/users/logout/');
    localStorage.removeItem('authToken');
};

// Management functions
export const getDashboard = async (): Promise<DashboardData> => {
    const response = await api.get<DashboardData>('/api/management/users/dashboard/');
    return response.data;
};

// Signup function
export const signup = async (payload: SignupPayload): Promise<SignupResponse> => {
    const response = await api.post<SignupResponse>('/api/management/users/signup/', payload);
    return response.data;
};

// User management functions
export const getUsers = async (): Promise<User[]> => {
    const response = await api.get<User[] | PaginatedResponse<User>>('/api/management/users/');
    const data = response.data;
    // Handle both array and paginated response
    if (Array.isArray(data)) {
        return data;
    }
    return data.results;
};

export const getUser = async (id: number): Promise<User> => {
    const response = await api.get<User>(`/api/management/users/${id}/`);
    return response.data;
};

export const createUser = async (data: UserCreatePayload): Promise<User> => {
    const response = await api.post<User>('/api/management/users/', data);
    return response.data;
};

export const updateUser = async (id: number, data: UserUpdatePayload): Promise<User> => {
    const response = await api.patch<User>(`/api/management/users/${id}/`, data);
    return response.data;
};

export const deleteUser = async (id: number): Promise<void> => {
    await api.delete(`/api/management/users/${id}/`);
};

// Company management (using API endpoint)
export const getCompanyAPI = async (): Promise<Company> => {
    const response = await api.get<Company>('/api/management/companies/me/');
    return response.data;
};

export const updateCompanyAPI = async (data: CompanyUpdatePayload): Promise<Company> => {
    const response = await api.patch<Company>('/api/management/companies/me/', data);
    return response.data;
};

// Campaign management functions
export const getCampaigns = async (): Promise<Campaign[]> => {
    const response = await api.get<Campaign[] | PaginatedResponse<Campaign>>('/api/management/campaigns/');
    const data = response.data;
    // Handle both array and paginated response
    if (Array.isArray(data)) {
        return data;
    }
    return data.results;
};

export const getCampaign = async (id: number): Promise<Campaign> => {
    const response = await api.get<Campaign>(`/api/management/campaigns/${id}/`);
    return response.data;
};

export const createCampaign = async (data: CampaignCreatePayload): Promise<Campaign> => {
    const response = await api.post<Campaign>('/api/management/campaigns/', data);
    return response.data;
};

export const updateCampaign = async (id: number, data: CampaignUpdatePayload): Promise<Campaign> => {
    const response = await api.patch<Campaign>(`/api/management/campaigns/${id}/`, data);
    return response.data;
};

export const deleteCampaign = async (id: number): Promise<void> => {
    await api.delete(`/api/management/campaigns/${id}/`);
};

// Tracking management functions
export const getTracking = async (): Promise<Tracking[]> => {
    const response = await api.get<Tracking[] | PaginatedResponse<Tracking>>('/api/management/tracking/');
    const data = response.data;
    // Handle both array and paginated response
    if (Array.isArray(data)) {
        return data;
    }
    return data.results;
};

export const getTrackingRecord = async (id: number): Promise<Tracking> => {
    const response = await api.get<Tracking>(`/api/management/tracking/${id}/`);
    return response.data;
};

export const createTracking = async (data: TrackingCreatePayload): Promise<Tracking> => {
    const response = await api.post<Tracking>('/api/management/tracking/', data);
    return response.data;
};

export const updateTracking = async (id: number, data: TrackingUpdatePayload): Promise<Tracking> => {
    const response = await api.patch<Tracking>(`/api/management/tracking/${id}/`, data);
    return response.data;
};

export const deleteTracking = async (id: number): Promise<void> => {
    await api.delete(`/api/management/tracking/${id}/`);
};

// Recipient management functions
export const getRecipients = async (): Promise<Recipient[]> => {
    const response = await api.get<Recipient[] | PaginatedResponse<Recipient>>('/api/management/recipients/');
    const data = response.data;
    // Handle both array and paginated response
    if (Array.isArray(data)) {
        return data;
    }
    return data.results;
};

export const getRecipient = async (id: number): Promise<Recipient> => {
    const response = await api.get<Recipient>(`/api/management/recipients/${id}/`);
    return response.data;
};

export const createRecipient = async (data: Partial<Recipient>): Promise<Recipient> => {
    const response = await api.post<Recipient>('/api/management/recipients/', data);
    return response.data;
};

export const updateRecipient = async (id: number, data: Partial<Recipient>): Promise<Recipient> => {
    const response = await api.patch<Recipient>(`/api/management/recipients/${id}/`, data);
    return response.data;
};

export const deleteRecipient = async (id: number): Promise<void> => {
    await api.delete(`/api/management/recipients/${id}/`);
};

// Request Data functions
export const getRequestData = async (id: number): Promise<RequestDataDetail> => {
    const response = await api.get<RequestDataDetail>(`/api/management/request-data/${id}/`);
    return response.data;
};

export interface RequestDataFilters {
    tracking_id: number;
    data_type?: string;
    http_method?: string;
    ip_address?: string;
    os?: string;
    browser?: string;
    platform?: string;
    locale?: string;
    server_timestamp?: string;
    client_time?: string;
    page?: number;
    page_size?: number;
    ordering?: string;
}

export const getRequestDataList = async (filters: RequestDataFilters): Promise<PaginatedResponse<RequestData>> => {
    const params = new URLSearchParams();
    params.append('tracking_id', filters.tracking_id.toString());
    if (filters.data_type) params.append('data_type', filters.data_type);
    if (filters.http_method) params.append('http_method', filters.http_method);
    if (filters.ip_address) params.append('ip_address', filters.ip_address);
    if (filters.os) params.append('os', filters.os);
    if (filters.browser) params.append('browser', filters.browser);
    if (filters.platform) params.append('platform', filters.platform);
    if (filters.locale) params.append('locale', filters.locale);
    if (filters.server_timestamp) params.append('server_timestamp', filters.server_timestamp);
    if (filters.client_time) params.append('client_time', filters.client_time);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const response = await api.get<PaginatedResponse<RequestData>>(`/api/management/request-data/?${params.toString()}`);
    return response.data;
};

export default api; 