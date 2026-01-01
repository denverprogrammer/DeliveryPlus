import axios from 'axios';
import type {
    Company,
    User,
    UserCreatePayload,
    UserUpdatePayload,
    Recipient,
    Campaign,
    CampaignCreatePayload,
    CampaignUpdatePayload,
    TrackingListItem,
    TrackingDetail,
    TrackingCreatePayload,
    TrackingUpdatePayload,
    CompanyUpdatePayload,
    LoginResponse,
    SignupResponse,
    SignupPayload,
    DashboardData,
    PaginatedResponse,
    PaginationParams,
    RequestData,
    RequestDataDetail,
    Token,
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
export const getUsers = async (): Promise<PaginatedResponse<User>> => {
    const response = await api.get<User[] | PaginatedResponse<User>>('/api/management/users/');
    const data = response.data;
    // Always return PaginatedResponse format
    if (Array.isArray(data)) {
        return {
            count: data.length,
            next: null,
            previous: null,
            results: data,
        };
    }
    return data;
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
export const getCampaigns = async (): Promise<PaginatedResponse<Campaign>> => {
    const response = await api.get<Campaign[] | PaginatedResponse<Campaign>>('/api/management/campaigns/');
    const data = response.data;
    // Always return PaginatedResponse format
    if (Array.isArray(data)) {
        return {
            count: data.length,
            next: null,
            previous: null,
            results: data,
        };
    }
    return data;
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
export const getTracking = async (): Promise<PaginatedResponse<TrackingListItem>> => {
    const response = await api.get<TrackingListItem[] | PaginatedResponse<TrackingListItem>>('/api/management/tracking/');
    const data = response.data;
    // Always return PaginatedResponse format
    if (Array.isArray(data)) {
        return {
            count: data.length,
            next: null,
            previous: null,
            results: data,
        };
    }
    return data;
};

export const getTrackingRecord = async (id: number): Promise<TrackingDetail> => {
    const response = await api.get<TrackingDetail>(`/api/management/tracking/${id}/`);
    return response.data;
};

export const createTracking = async (data: TrackingCreatePayload): Promise<TrackingDetail> => {
    const response = await api.post<TrackingDetail>('/api/management/tracking/', data);
    return response.data;
};

export const updateTracking = async (id: number, data: TrackingUpdatePayload): Promise<TrackingDetail> => {
    const response = await api.patch<TrackingDetail>(`/api/management/tracking/${id}/`, data);
    return response.data;
};

export const deleteTracking = async (id: number): Promise<void> => {
    await api.delete(`/api/management/tracking/${id}/`);
};

// Recipient management functions
export const getRecipients = async (): Promise<PaginatedResponse<Recipient>> => {
    const response = await api.get<Recipient[] | PaginatedResponse<Recipient>>('/api/management/recipients/');
    const data = response.data;
    // Always return PaginatedResponse format
    if (Array.isArray(data)) {
        return {
            count: data.length,
            next: null,
            previous: null,
            results: data,
        };
    }
    return data;
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

export interface RequestDataFilters extends PaginationParams {
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
}

export const getRequestDataList = async (filters: RequestDataFilters): Promise<PaginatedResponse<RequestData>> => {
    const params = new URLSearchParams();
    params.append('tracking_id', filters.tracking_id.toString());
    
    // Handle filters from PaginationParams.filters (spread in TrackingDetail) or direct filter fields
    const filterFields = filters.filters || {};
    if (filters.data_type ?? filterFields.data_type) params.append('data_type', String(filters.data_type ?? filterFields.data_type));
    if (filters.http_method ?? filterFields.http_method) params.append('http_method', String(filters.http_method ?? filterFields.http_method));
    if (filters.ip_address ?? filterFields.ip_address) params.append('ip_address', String(filters.ip_address ?? filterFields.ip_address));
    if (filters.os ?? filterFields.os) params.append('os', String(filters.os ?? filterFields.os));
    if (filters.browser ?? filterFields.browser) params.append('browser', String(filters.browser ?? filterFields.browser));
    if (filters.platform ?? filterFields.platform) params.append('platform', String(filters.platform ?? filterFields.platform));
    if (filters.locale ?? filterFields.locale) params.append('locale', String(filters.locale ?? filterFields.locale));
    if (filters.server_timestamp ?? filterFields.server_timestamp) params.append('server_timestamp', String(filters.server_timestamp ?? filterFields.server_timestamp));
    if (filters.client_time ?? filterFields.client_time) params.append('client_time', String(filters.client_time ?? filterFields.client_time));
    
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const response = await api.get<PaginatedResponse<RequestData>>(`/api/management/request-data/?${params.toString()}`);
    return response.data;
};

// Token functions
export interface TokenFilters extends PaginationParams {
    tracking_id: number;
}

export const getTokenList = async (filters: TokenFilters): Promise<PaginatedResponse<Token>> => {
    const params = new URLSearchParams();
    params.append('tracking_id', filters.tracking_id.toString());
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.page_size) params.append('page_size', filters.page_size.toString());
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const response = await api.get<PaginatedResponse<Token>>(`/api/management/tokens/?${params.toString()}`);
    return response.data;
};

export const disableToken = async (id: number): Promise<Token> => {
    const response = await api.post<Token>(`/api/management/tokens/${id}/disable/`);
    return response.data;
};

export const reactivateToken = async (id: number): Promise<Token> => {
    const response = await api.post<Token>(`/api/management/tokens/${id}/reactivate/`);
    return response.data;
};

export const createToken = async (trackingId: number): Promise<Token> => {
    const response = await api.post<Token>('/api/management/tokens/create_token/', {
        tracking_id: trackingId,
    });
    return response.data;
};

export default api;

