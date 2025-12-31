// Component Props Interfaces
export interface LayoutProps {
    children: React.ReactNode;
}

export interface SidebarProps {
    onToggle?: (collapsed: boolean) => void;
}

export interface BreadcrumbItem {
    label: string;
    path: string;
}

export interface RequestDataModalProps {
    show: boolean;
    onHide: () => void;
    requestDataId: number | null;
}

// Note: Campaign and Recipient types are available from './api'
// Use those types directly instead of creating simplified versions

