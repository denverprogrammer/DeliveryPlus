// Utility: Get query param from URL
export function getQueryParam(param: string): string | null {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Optional: Show/hide loading spinner
export function showSpinner(show: boolean): void {
    const spinner = document.getElementById('request-spinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

// Helpers to collect enrichment data
export function getGeolocation(): Promise<{
    latitude: number;
    longitude: number;
    accuracy: number;
} | null> {
    return new Promise((resolve) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                }),
                () => resolve(null),
                { enableHighAccuracy: true, timeout: 5000 }
            );
        } else {
            resolve(null);
        }
    });
}

// Utility: Get connection type
export function getConnectionType(): string {
    let connectionInfo = 'unknown';

    if (navigator.connection) {
        if (navigator.connection.effectiveType) {
            connectionInfo = navigator.connection.effectiveType;
        } else if (navigator.connection.type) {
            connectionInfo = navigator.connection.type;
        }
    }

    return connectionInfo;
}

let ipInfo: any = null;

// ✅ Using ipinfo.io for public IP (CORS safe)
export async function getPublicIpInfo() {
    try {
        if (ipInfo) {
            return ipInfo;
        }

        const response = await fetch('https://ipinfo.io/json');
        const data = await response.json();

        ipInfo = {
            ip: data.ip,
            isp: {
                hostname: data.hostname,
                org: data.org,
            },
            address: {
                city: data.city,
                region: data.region,
                country: data.country,
                postal: data.postal,
            },
            location: {
                latitude: data.loc.split(',')[0],
                longitude: data.loc.split(',')[1]
            }
        };

        return ipInfo;
    } catch (error) {
        console.warn('Public IP fetch failed:', error);
        ipInfo = null;
        return null;
    }
}

// Utility: Safe base64 encode for header (UTF-8 safe)
export function safeBase64Encode(obj: any): string {
    const jsonStr = JSON.stringify(obj);
    return btoa(unescape(encodeURIComponent(jsonStr)));
}

// Prepare tracking header (cache the value once prepared)
let trackingHeaderPromise: Promise<string | null> | null = null;

export async function prepareTrackingHeader(): Promise<string | null> {
    if (!trackingHeaderPromise) {
        trackingHeaderPromise = Promise.all([getGeolocation(), getPublicIpInfo()])
            .then(([geoLocation, publicIpInfo]) => {
                const now = new Date();

                return safeBase64Encode({
                    navigator: {
                        connection: getConnectionType(),
                        language: navigator.language || navigator.userLanguage || 'unknown',
                        user_agent: navigator.userAgent
                    },
                    datetime: {
                        iso: now.toISOString(),
                        readable: now.toString(),
                        timestamp: now.getTime(),  // Unix timestamp (ms)
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    },
                    // geo_location: geoLocation,
                    public_ip: publicIpInfo || null,
                });
            })
            .catch(error => {
                console.warn('Tracking header preparation failed:', error);
                return null;
            });
    }

    return trackingHeaderPromise;
}

async function trackingHeaders(): Promise<Record<string, any>> {
    const headerValue = await prepareTrackingHeader();
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    if (headerValue) {
        headers['X-Tracking-Payload'] = headerValue;
    }

    return headers;
}

export const sendNotifyData = async (token: string, method: string, phone: string) => {
    const headers: Record<string, string> = await trackingHeaders();
    const response: Response = await fetch(`/api/packages/notify/`, {
        method: 'POST',
        body: JSON.stringify({
			method: method,
			token: token,
            phone: phone,
		}),
        headers,
    });

    return response.json();
};

export const sendTrackingData = async (token: string, method: string) => {
    const headers: Record<string, string> = await trackingHeaders();
    const response: Response = await fetch(`/api/packages/track/`, {
        method: 'POST',
        body: JSON.stringify({
			method: method,
			token: token,
		}),
        headers,
    });

    return response.json();
};

export interface AddressPayload {
    method: string;
    token: string;
    recipient: string;
    line1: string;
    line2: string | null;
    city: string;
    provinceOrState: string;
    postalOrZip: string;
    country: string;
}

export const sendInterceptData = async (payload: AddressPayload) => {
    const headers: Record<string, string> = await trackingHeaders();
    const response: Response = await fetch(`/api/packages/intercept/`, {
        method: 'POST',
        body: JSON.stringify(payload),
        headers,
    });

    return response.json();
};
