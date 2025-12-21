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
    formData.append('image', file);

    const headers: Record<string, string> = {};

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    const response = await fetch('/api/images/', {
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

