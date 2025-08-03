import React, { useEffect, useState } from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import { getDashboard } from '../shared/services/api';

interface DashboardData {
    company: {
        name: string;
        // Add other company fields as needed
    };
}

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
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <h5 className="mb-0">Company Information</h5>
                        </Card.Header>
                        <Card.Body>
                            <p><strong>Company:</strong> {dashboardData?.company?.name}</p>
                            {/* Add more company information as needed */}
                        </Card.Body>
                    </Card>
                </Col>
                
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <h5 className="mb-0">Quick Actions</h5>
                        </Card.Header>
                        <Card.Body>
                            <p>This is a test dashboard. Add more functionality as needed.</p>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Dashboard; 