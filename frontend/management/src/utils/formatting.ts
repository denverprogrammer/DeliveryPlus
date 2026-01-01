/**
 * Formats a date string to a localized string representation.
 * Returns null if the date string is undefined or empty.
 * 
 * @param dateString - The date string to format
 * @returns Formatted date string or null
 */
export const formatDate = (dateString: string | undefined | null): string|null => {
    try {
        if (dateString) {
            return new Date(dateString).toLocaleString();
        }
    } catch {}

    return null;
};

/**
 * Formats a coordinate value (latitude/longitude) to 4 decimal places.
 * Returns null if the value is undefined.
 * 
 * @param value - The coordinate value to format
 * @returns Formatted coordinate string or null.
 */
export const formatCoordinate = (value: number | undefined | null): string | null => {
    if (value) {
        return value.toFixed(4);
    }
    
    return null;
};

export const formatDateTime = (dateString: string | undefined | null): string[] | null => {
    try {
        if (dateString) {
            const date = new Date(dateString);
            const datePart = date.toLocaleDateString();
            const timePart = date.toLocaleTimeString();

            return [datePart, timePart];
        }
    } catch {}

    return null;
};
