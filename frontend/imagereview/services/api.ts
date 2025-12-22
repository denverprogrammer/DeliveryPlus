import { prepareTrackingHeader } from '../../shared/services/trackingUtils';

export interface UploadImageResponse {
    status: string;
    detail?: string;
    error?: string;
}

export const uploadImage = async (token: string, file: File): Promise<UploadImageResponse> => {
    const headerValue = await prepareTrackingHeader();
    
    const formData = new FormData();
    formData.append('token', token);
    formData.append('method', 'POST');
    formData.append('image', file);

    const headers: Record<string, string> = {};

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch('/api/images/upload/', {
        method: 'POST',
        body: formData,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to upload image' }));
        throw new Error(errorData.detail || errorData.error || 'Failed to upload image');
    }

    return response.json();
};

export const checkToken = async (token: string): Promise<UploadImageResponse> => {
    const headerValue = await prepareTrackingHeader();

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch('/api/images/track/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
            token,
            method: 'GET',
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to get token' }));
        throw new Error(errorData.detail || errorData.error || 'Failed to get token');
    }

    return response.json();
};

