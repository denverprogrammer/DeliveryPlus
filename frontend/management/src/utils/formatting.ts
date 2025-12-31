import { NOT_AVAILABLE } from '../constants/ui';

/**
 * Formats a date string to a localized string representation.
 * Returns NOT_AVAILABLE if the date string is undefined or empty.
 * 
 * @param dateString - The date string to format
 * @returns Formatted date string or NOT_AVAILABLE
 */
export const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return NOT_AVAILABLE;
    try {
        return new Date(dateString).toLocaleString();
    } catch {
        return dateString;
    }
};

/**
 * Formats a coordinate value (latitude/longitude) to 4 decimal places.
 * Returns NOT_AVAILABLE if the value is undefined.
 * 
 * @param value - The coordinate value to format
 * @returns Formatted coordinate string or NOT_AVAILABLE
 */
export const formatCoordinate = (value: number | undefined): string => {
    if (value === undefined) return NOT_AVAILABLE;
    return value.toFixed(4);
};
