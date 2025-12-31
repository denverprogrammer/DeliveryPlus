import React from 'react';

/**
 * Gets the Bootstrap alert class name based on warning status.
 * 
 * @param status - The warning status ('success', 'warning', 'danger', or undefined)
 * @returns Bootstrap alert class name
 */
export const getWarningClass = (status: string | undefined): string => {
    switch (status) {
        case 'success':
            return 'success';
        case 'warning':
            return 'warning';
        case 'danger':
            return 'danger';
        default:
            return 'warning';
    }
};

/**
 * Renders an alert with a unique ID.
 * 
 * @param alertId - Unique identifier for the alert element
 * @param warning - Warning object with status and message, or undefined
 * @returns React element or null
 */
export const renderAlert = (alertId: string, warning: { status: string; message: string } | undefined): React.ReactElement | null => {
    if (!warning) return null;
    return (
        <div id={alertId} className={`alert alert-${getWarningClass(warning.status)}`}>
            {warning.message}
        </div>
    );
};
