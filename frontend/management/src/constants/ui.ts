// UI Constants
export const SIDEBAR_WIDTH = {
    EXPANDED: '250px',
    COLLAPSED: '60px',
} as const;

export const NAVBAR_HEIGHT = '56px';

export const COLORS = {
    PRIMARY: '#0d6efd',
    SECONDARY: '#6c757d',
    SUCCESS: '#198754',
    DANGER: '#dc3545',
    WARNING: '#ffc107',
    INFO: '#0dcaf0',
    LIGHT: '#f8f9fa',
    DARK: '#212529',
    MUTED: '#6c757d',
    BORDER: '#dee2e6',
    HOVER_BG: '#e9ecef',
} as const;

export const ROUTES = {
    DASHBOARD: '/dashboard',
    USERS: '/users',
    CAMPAIGNS: '/campaigns',
    TRACKING: '/tracking',
    RECIPIENTS: '/recipients',
    COMPANY_EDIT: '/company/edit',
    LOGIN: '/login',
    SIGNUP: '/signup',
} as const;

export const MENU_ITEMS = [
    { path: ROUTES.USERS, label: 'Manage Users', icon: '👥' },
    { path: ROUTES.CAMPAIGNS, label: 'Manage Campaigns', icon: '📢' },
    { path: ROUTES.TRACKING, label: 'Manage Tracking', icon: '📊' },
    { path: ROUTES.COMPANY_EDIT, label: 'Edit Company', icon: '🏢' },
] as const;

export const TRANSITION_DURATION = {
    FAST: '0.2s',
    NORMAL: '0.3s',
    SLOW: '0.5s',
} as const;

export const DEBOUNCE_DELAY = 300;

export const TABLE_CAPTION_STYLE = {
    captionSide: 'top' as const,
    fontWeight: 'bold',
    fontSize: '1.25rem',
    marginBottom: '0.5rem',
};

export const SORT_ICON_STYLE = {
    fontSize: '1.2em',
    fontWeight: 'bold',
} as const;

export const FILTER_INPUT_MIN_WIDTH = {
    SMALL: '100px',
    MEDIUM: '120px',
} as const;

export const NOT_AVAILABLE = 'N/A';

