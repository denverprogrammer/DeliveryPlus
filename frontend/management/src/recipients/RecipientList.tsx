import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, Alert } from 'react-bootstrap';
import { getRecipients } from '../services/api';
import type { Recipient } from '../types/api';
import { isNonEmptyArray } from '../utils/typeGuards';

const RecipientList = () => {
    const [recipients, setRecipients] = useState<Recipient[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRecipients = async () => {
            try {
                const data = await getRecipients();
                setRecipients(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load recipients');
            } finally {
                setIsLoading(false);
            }
        };

        fetchRecipients();
    }, []);

    if (isLoading) {
        return <div>Loading recipients...</div>;
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h2>Recipients List</h2>
                <Link to="/recipients/add" className="btn btn-primary">
                    Add Recipient
                </Link>
            </div>

            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {isNonEmptyArray(recipients) ? (
                        recipients.map((recipient) => (
                            <tr key={recipient.id}>
                                <td>{recipient.first_name} {recipient.last_name}</td>
                                <td>{recipient.email}</td>
                                <td>{recipient.status || 'N/A'}</td>
                                <td>
                                    <Link 
                                        to={`/recipients/${recipient.id}/edit`}
                                        className="btn btn-outline-primary btn-sm"
                                    >
                                        Edit
                                    </Link>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan={4} className="text-center">
                                No recipients found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </Table>
        </div>
    );
};

export default RecipientList;
