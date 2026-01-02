import { useEffect, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Breadcrumb } from 'react-bootstrap';
import { getCampaign, getUser, getTrackingDetail } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { BreadcrumbItem } from '../types';

const Breadcrumbs = () => {
    const location = useLocation();
    const { isAuthenticated } = useAuth();
    const [items, setItems] = useState<BreadcrumbItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const buildBreadcrumbs = async () => {
            if (!isAuthenticated) {
                setItems([]);
                setIsLoading(false);
                return;
            }

            const path = location.pathname;
            const breadcrumbs: BreadcrumbItem[] = [];

            // Parse the path
            const segments = path.split('/').filter(Boolean);

            // Handle special cases first
            if (segments.length === 0 || (segments.length === 1 && segments[0] === 'dashboard')) {
                // On dashboard - show just Dashboard
                breadcrumbs.push({ label: 'Dashboard', path: '/dashboard' });
            } else if (segments[0] === 'users') {
                // Always start with Dashboard for non-dashboard pages
                breadcrumbs.push({ label: 'Dashboard', path: '/dashboard' });
                breadcrumbs.push({ label: 'Users', path: '/users' });
                if (segments.length > 1) {
                    if (segments[1] === 'add') {
                        breadcrumbs.push({ label: 'Add User', path: '/users/add' });
                    } else if (!isNaN(Number(segments[1]))) {
                        try {
                            const user = await getUser(parseInt(segments[1]));
                            const userPath = `/users/${segments[1]}`;
                            breadcrumbs.push({ 
                                label: user.username || `User #${segments[1]}`, 
                                path: userPath 
                            });
                            if (segments.length > 2 && segments[2] === 'edit') {
                                breadcrumbs.push({ label: 'Edit', path: `${userPath}/edit` });
                            }
                        } catch {
                            const userPath = `/users/${segments[1]}`;
                            breadcrumbs.push({ label: `User #${segments[1]}`, path: userPath });
                            if (segments.length > 2 && segments[2] === 'edit') {
                                breadcrumbs.push({ label: 'Edit', path: `${userPath}/edit` });
                            }
                        }
                    }
                }
            } else if (segments[0] === 'campaigns') {
                // Always start with Dashboard for non-dashboard pages
                breadcrumbs.push({ label: 'Dashboard', path: '/dashboard' });
                breadcrumbs.push({ label: 'Campaigns', path: '/campaigns' });
                if (segments.length > 1) {
                    if (segments[1] === 'add') {
                        breadcrumbs.push({ label: 'Add Campaign', path: '/campaigns/add' });
                    } else if (!isNaN(Number(segments[1]))) {
                        const campaignId = segments[1];
                        try {
                            const campaign = await getCampaign(parseInt(campaignId));
                            const campaignPath = `/campaigns/${campaignId}`;
                            breadcrumbs.push({ 
                                label: campaign.name || `Campaign #${campaignId}`, 
                                path: campaignPath 
                            });
                            if (segments.length > 2) {
                                if (segments[2] === 'edit') {
                                    breadcrumbs.push({ label: 'Edit', path: `${campaignPath}/edit` });
                                } else if (segments[2] === 'tracking') {
                                    // Tracking nested under campaign
                                    const trackingPath = `${campaignPath}/tracking`;
                                    breadcrumbs.push({ label: 'Tracking', path: trackingPath });
                                    if (segments.length > 3) {
                                        if (segments[3] === 'add') {
                                            breadcrumbs.push({ label: 'Add Tracking', path: `${trackingPath}/add` });
                                        } else if (!isNaN(Number(segments[3]))) {
                                            try {
                                                const tracking = await getTrackingDetail(parseInt(segments[3]));
                                                const trackingDetailPath = `${trackingPath}/${segments[3]}`;
                                                const label = tracking.recipient?.full_name || `Tracking #${segments[3]}`;
                                                breadcrumbs.push({ label, path: trackingDetailPath });
                                                if (segments.length > 4 && segments[4] === 'edit') {
                                                    breadcrumbs.push({ label: 'Edit', path: `${trackingDetailPath}/edit` });
                                                }
                                            } catch {
                                                const trackingDetailPath = `${trackingPath}/${segments[3]}`;
                                                breadcrumbs.push({ label: `Tracking #${segments[3]}`, path: trackingDetailPath });
                                                if (segments.length > 4 && segments[4] === 'edit') {
                                                    breadcrumbs.push({ label: 'Edit', path: `${trackingDetailPath}/edit` });
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } catch {
                            const campaignPath = `/campaigns/${campaignId}`;
                            breadcrumbs.push({ label: `Campaign #${campaignId}`, path: campaignPath });
                            if (segments.length > 2) {
                                if (segments[2] === 'edit') {
                                    breadcrumbs.push({ label: 'Edit', path: `${campaignPath}/edit` });
                                } else if (segments[2] === 'tracking') {
                                    const trackingPath = `${campaignPath}/tracking`;
                                    breadcrumbs.push({ label: 'Tracking', path: trackingPath });
                                    if (segments.length > 3) {
                                        if (segments[3] === 'add') {
                                            breadcrumbs.push({ label: 'Add Tracking', path: `${trackingPath}/add` });
                                        } else if (!isNaN(Number(segments[3]))) {
                                            const trackingDetailPath = `${trackingPath}/${segments[3]}`;
                                            breadcrumbs.push({ label: `Tracking #${segments[3]}`, path: trackingDetailPath });
                                            if (segments.length > 4 && segments[4] === 'edit') {
                                                breadcrumbs.push({ label: 'Edit', path: `${trackingDetailPath}/edit` });
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } else if (segments[0] === 'tracking') {
                // Top-level tracking routes
                // Always start with Dashboard for non-dashboard pages
                breadcrumbs.push({ label: 'Dashboard', path: '/dashboard' });
                breadcrumbs.push({ label: 'Tracking', path: '/tracking' });
                if (segments.length > 1) {
                    if (segments[1] === 'add') {
                        breadcrumbs.push({ label: 'Add Tracking', path: '/tracking/add' });
                    } else if (!isNaN(Number(segments[1]))) {
                        // This is a tracking ID - show just the ID number
                        const trackingId = segments[1];
                        if (segments.length > 2 && segments[2] === 'edit') {
                            breadcrumbs.push({ label: trackingId, path: `/tracking/${trackingId}` });
                            breadcrumbs.push({ label: 'Edit', path: `/tracking/${trackingId}/edit` });
                        } else {
                            breadcrumbs.push({ label: trackingId, path: `/tracking/${trackingId}` });
                        }
                    }
                }
            } else if (segments[0] === 'company') {
                // Always start with Dashboard for non-dashboard pages
                breadcrumbs.push({ label: 'Dashboard', path: '/dashboard' });
                breadcrumbs.push({ label: 'Company', path: '/company/edit' });
            } else if (segments[0] === 'login') {
                breadcrumbs.push({ label: 'Login', path: '/login' });
            } else if (segments[0] === 'signup') {
                breadcrumbs.push({ label: 'Sign Up', path: '/signup' });
            }

            setItems(breadcrumbs);
            setIsLoading(false);
        };

        buildBreadcrumbs();
    }, [location.pathname, isAuthenticated]);

    if (!isAuthenticated || isLoading || items.length === 0) {
        return null;
    }

    return (
        <Breadcrumb className="mb-3">
            {items.map((item, index) => {
                const isLast = index === items.length - 1;
                return (
                    <Breadcrumb.Item
                        key={item.path}
                        active={isLast}
                        linkAs={isLast ? 'span' : Link}
                        linkProps={isLast ? {} : { to: item.path }}
                    >
                        {item.label}
                    </Breadcrumb.Item>
                );
            })}
        </Breadcrumb>
    );
};

export default Breadcrumbs;

