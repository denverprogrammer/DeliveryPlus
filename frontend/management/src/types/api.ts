// API Response Types

export interface Company {
    id: number;
    name: string;
    street_address: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
    phone_number: string;
}

export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
    is_staff: boolean;
    company?: number | Company;
}

export interface UserCreatePayload {
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    password?: string;
    is_active?: boolean;
    is_staff?: boolean;
}

export interface UserUpdatePayload {
    username?: string;
    email?: string;
    first_name?: string;
    last_name?: string;
    password?: string;
    is_active?: boolean;
    is_staff?: boolean;
}

export interface RecipientTag {
    id: number;
    name: string;
}

export interface Recipient {
    id: number;
    first_name: string;
    last_name: string;
    full_name: string;
    email: string;
    phone_number?: string;
    status?: string;
    tags?: RecipientTag[];
    company?: number | Company;
}

export interface Token {
    id: number;
    value: string;
    status: string;
    created_on: string;
    last_used?: string | null;
    deleted_on?: string | null;
    used?: number | string;
}

export interface RequestData {
    id: number;
    data_type: string;
    http_method: string;
    server_timestamp: string;
    ip_address?: string;
    ip_source?: string;
    os?: string;
    browser?: string;
    platform?: string;
    locale?: string;
    client_time?: string;
    client_timezone?: string;
    latitude?: number;
    longitude?: number;
    location_source?: string;
}

export interface RequestDataDetail extends RequestData {
    organization?: string;
    isp?: string;
    country?: string;
    region?: string;
    city?: string;
    _ip_data?: Record<string, any>;
    _user_agent_data?: Record<string, any>;
    _header_data?: Record<string, any>;
    _form_data?: Record<string, any>;
    warnings: {
        security_checks?: Array<{ status: string; message: string }>;
        ip_mismatch?: { status: string; message: string };
        country_mismatch?: { status: string; message: string };
        user_agent_mismatch?: { status: string; message: string };
        timezone_mismatch?: { status: string; message: string };
        locale_mismatch?: { status: string; message: string };
        crawler_detection?: { status: string; message: string };
    };
    image_url?: string;
    image?: string;
    altitude?: number;
    make?: string;
    model?: string;
    software?: string;
    width?: number;
    height?: number;
    orientation?: number;
    datetime_original?: string;
    datetime_digitized?: string;
    exposure_time?: string;
    f_number?: number;
    iso_speed?: number;
    focal_length?: number;
    flash?: boolean;
    raw_exif_data?: Record<string, any>;
}

export interface TrackingListItem {
    id: number;
    campaign: Campaign;
    recipient: Recipient | null;
    company: number | Company;
    count_requests: number;
}

export interface TrackingDetail {
    id: number;
    tokens: Token[];
    token_values: string[];
    campaign: Campaign;
    recipient: Recipient | null;
    company: number | Company;
    count_requests: number;
    request_data?: RequestData[];
}

// Keep Tracking as alias for backward compatibility
export type Tracking = TrackingDetail;

export interface TrackingCreatePayload {
    campaign: number;
    recipient?: number | null;
}

export interface TrackingUpdatePayload {
    campaign?: number;
    recipient?: number | null;
}

export interface Campaign {
    id: number;
    name: string;
    description?: string;
    campaign_type: string;
    publishing_type?: string[];
    landing_page_url?: string;
    tracking_pixel?: string;
    ip_precedence?: string;
    location_precedence?: string;
    locale_precedence?: string;
    browser_precedence?: string;
    time_precedence?: string;
    ip_tracking?: string[];
    location_tracking?: string[];
    locale_tracking?: string[];
    browser_tracking?: string[];
    time_tracking?: string[];
    company?: number | Company;
}

export interface CampaignCreatePayload {
    name: string;
    description?: string;
    campaign_type: string;
    publishing_type?: string[];
    landing_page_url?: string;
    tracking_pixel?: string;
    ip_precedence?: string;
    location_precedence?: string;
    locale_precedence?: string;
    browser_precedence?: string;
    time_precedence?: string;
    ip_tracking?: string[];
    location_tracking?: string[];
    locale_tracking?: string[];
    browser_tracking?: string[];
    time_tracking?: string[];
}

export interface CampaignUpdatePayload {
    name?: string;
    description?: string;
    campaign_type?: string;
    publishing_type?: string[];
    landing_page_url?: string;
    tracking_pixel?: string;
    ip_precedence?: string;
    location_precedence?: string;
    locale_precedence?: string;
    browser_precedence?: string;
    time_precedence?: string;
    ip_tracking?: string[];
    location_tracking?: string[];
    locale_tracking?: string[];
    browser_tracking?: string[];
    time_tracking?: string[];
}

export interface CompanyUpdatePayload {
    name?: string;
    street_address?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    country?: string;
    phone_number?: string;
}

// Auth response types
export interface LoginResponse {
    success: boolean;
    user: User;
}

export interface SignupResponse {
    success: boolean;
    user: {
        id: number;
        username: string;
        email: string;
        company: string | null;
    };
}

export interface SignupPayload {
    username: string;
    email: string;
    password1: string;
    password2: string;
    company_name: string;
}

export interface LoginPayload {
    username: string;
    password: string;
}

// Dashboard response
export interface DashboardData {
    company: {
        name: string;
    };
}

// API Error response
export interface ApiError {
    errors?: Record<string, string[]>;
    error?: string;
    detail?: string;
}

// Paginated response (DRF default)
export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

