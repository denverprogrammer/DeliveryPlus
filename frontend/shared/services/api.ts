import axios from 'axios';
import { prepareTrackingHeader } from './trackingUtils';

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

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
export const sendTrackingData = async (token: string) => {
    const headerValue = await prepareTrackingHeader();
    
    const formData = new FormData();
    formData.append('http_method', 'POST');
    formData.append('token', token);

    const headers: Record<string, string> = {
        'Content-Type': 'multipart/form-data',
    };

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch(`${API_BASE_URL}/tracking/${token}/`, {
        method: 'POST',
        body: formData,
        headers,
    });

    return response.json();
};

export const sendRedirectData = async (token: string, notifications?: string) => {
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

    const response = await fetch(`${API_BASE_URL}/tracking/redirects/${token}/`, {
        method: 'POST',
        body: formData,
        headers,
    });

    return response.json();
};

// Auth functions
export const login = async (username: string, password: string) => {
    const response = await api.post('/mgmt/login/', { username, password });
    return response.data;
};

export const logout = async () => {
    await api.post('/mgmt/logout/');
    localStorage.removeItem('authToken');
};

// Management functions
export const getDashboard = async () => {
    const response = await api.get('/mgmt/');
    return response.data;
};

export const getAgents = async () => {
    const response = await api.get('/mgmt/agents/');
    return response.data;
};

export const getAgent = async (id: number) => {
    const response = await api.get(`/mgmt/agents/${id}/`);
    return response.data;
};

export const createAgent = async (data: any) => {
    const response = await api.post('/mgmt/agents/add/', data);
    return response.data;
};

export const updateAgent = async (id: number, data: any) => {
    const response = await api.put(`/mgmt/agents/${id}/edit/`, data);
    return response.data;
};

export const getCompany = async () => {
    const response = await api.get('/mgmt/company/edit/');
    return response.data;
};

export const updateCompany = async (data: any) => {
    const response = await api.put('/mgmt/company/edit/', data);
    return response.data;
};

export default api; 