import { useEffect, useState } from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import { getDashboard } from './services/api';
import type { DashboardData } from './types/api';

const Dashboard = () => {
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const data = await getDashboard();
                setDashboardData(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load dashboard');
            } finally {
                setIsLoading(false);
            }
        };

        fetchDashboard();
    }, []);

    if (isLoading) {
        return <div>Loading dashboard...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    return (
        <div>
            <h2 className="mb-4">Dashboard</h2>
            
            <Row>
                <Col md={12}>
                    <Card>
                        <Card.Header>
                            <h5 className="mb-0">Company Information</h5>
                        </Card.Header>
                        <Card.Body>
                            <p><strong>Company:</strong> {dashboardData?.company?.name || 'No Company'}</p>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Dashboard; 