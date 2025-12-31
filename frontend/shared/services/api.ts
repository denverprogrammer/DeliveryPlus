import { prepareTrackingHeader } from './trackingUtils';

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
