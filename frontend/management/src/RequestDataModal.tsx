import React, { useEffect, useState, useRef } from 'react';
import { Modal, Tabs, Tab } from 'react-bootstrap';
import { getRequestData } from './services/api';
import type { RequestDataDetail } from './types/api';
import type { RequestDataModalProps } from './types';
import { NOT_AVAILABLE } from './constants/ui';
import { formatDate, formatCoordinate } from './utils/formatting';
import { renderAlert } from './utils/alerts';
import { isNonEmptyArray } from './utils/typeGuards';

// Declare JSONEditor type
declare global {
    interface Window {
        JSONEditor: any;
    }
}

const RequestDataModal: React.FC<RequestDataModalProps> = ({ show, onHide, requestDataId }) => {
    const [data, setData] = useState<RequestDataDetail | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<string>('details');
    const jsonEditorRefs = useRef<Record<string, any>>({});

    useEffect(() => {
        if (show && requestDataId) {
            loadData();
        } else {
            setData(null);
            setError(null);
            setActiveTab('details');
        }
    }, [show, requestDataId]);

    useEffect(() => {
        if (data && show && window.JSONEditor) {
            // Small delay to ensure DOM is ready when tab switches
            const timer = setTimeout(() => {
                initializeJSONEditors();
            }, 100);
            return () => {
                clearTimeout(timer);
            };
        }
        return () => {
            // Cleanup JSON editors
            Object.values(jsonEditorRefs.current).forEach((editor: any) => {
                if (editor && editor.destroy) {
                    editor.destroy();
                }
            });
            jsonEditorRefs.current = {};
        };
    }, [data, show, activeTab]);

    const loadData = async () => {
        if (!requestDataId) return;
        try {
            setIsLoading(true);
            setError(null);
            const response = await getRequestData(requestDataId);
            setData(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load request data');
        } finally {
            setIsLoading(false);
        }
    };

    const initializeJSONEditors = () => {
        if (!window.JSONEditor || !data) return;

        const jsonFields = ['_ip_data', '_user_agent_data', '_header_data', '_form_data'];
        
        jsonFields.forEach((fieldName) => {
            const containerId = `${fieldName}-editor`;
            const container = document.getElementById(containerId);
            
            if (!container) return;
            
            // Destroy existing editor if it exists
            if (jsonEditorRefs.current[fieldName]) {
                try {
                    jsonEditorRefs.current[fieldName].destroy();
                } catch (e) {
                    console.warn(`Error destroying editor for ${fieldName}:`, e);
                }
                delete jsonEditorRefs.current[fieldName];
            }

            const jsonData = data[fieldName as keyof RequestDataDetail] as Record<string, any> | undefined;
            if (!jsonData) return;

            try {
                const options = {
                    mode: 'view' as const,
                    mainMenuBar: false,
                    navigationBar: false,
                    statusBar: false,
                    search: false,
                    enableSort: false,
                    enableTransform: false,
                    colorPicker: false,
                    modeSwitcher: false,
                    onEditable: () => false,
                };

                const editor = new window.JSONEditor(container, options);
                editor.set(jsonData);
                jsonEditorRefs.current[fieldName] = editor;
            } catch (e) {
                console.error(`Failed to initialize JSONEditor for ${fieldName}:`, e);
            }
        });
    };

    const renderSecurityChecks = (requestData: RequestDataDetail) => {
        return (
            <>
                <h5>Security Checks</h5>
                {isNonEmptyArray(requestData.warnings.security_checks) ? (
                    requestData.warnings.security_checks.map((warning, idx) => (
                        <React.Fragment key={idx}>
                            {renderAlert(`security-check-${idx}`, warning)}
                        </React.Fragment>
                    ))
                ) : (
                    <p className="text-muted">No security checks available.</p>
                )}
            </>
        );
    };

    const renderIPAndHeaderConsistency = (requestData: RequestDataDetail) => {
        return (
            <>
                <h5 className="mt-3">IP and Header Consistency</h5>
                {renderAlert('ip-mismatch-alert', requestData.warnings.ip_mismatch)}
                {renderAlert('country-mismatch-alert', requestData.warnings.country_mismatch)}
                {renderAlert('timezone-mismatch-alert', requestData.warnings.timezone_mismatch)}
                {renderAlert('locale-mismatch-alert', requestData.warnings.locale_mismatch)}
            </>
        );
    };

    const renderBrowserAndClientChecks = (requestData: RequestDataDetail) => {
        return (
            <>
                <h5 className="mt-3">Browser and Client Checks</h5>
                {renderAlert('user-agent-mismatch-alert', requestData.warnings.user_agent_mismatch)}
                {renderAlert('crawler-detection-alert', requestData.warnings.crawler_detection)}
            </>
        );
    };

    if (!show) return null;

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>
            <Modal.Header closeButton>
                <Modal.Title>Request Data Details</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {isLoading && <div>Loading...</div>}
                {error && <div className="alert alert-danger">{error}</div>}
                {data && (
                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <style>{`
                            .modal-body .nav-tabs .nav-link {
                                color: #495057 !important;
                                background-color: transparent !important;
                                border: 1px solid transparent !important;
                                border-top-left-radius: 0.25rem;
                                border-top-right-radius: 0.25rem;
                            }
                            .modal-body .nav-tabs .nav-link:hover {
                                color: #495057 !important;
                                border-color: #e9ecef #e9ecef #dee2e6 !important;
                            }
                            .modal-body .nav-tabs .nav-link.active {
                                color: #495057 !important;
                                background-color: #fff !important;
                                border-color: #dee2e6 #dee2e6 #fff !important;
                            }
                        `}</style>
                        <Tabs 
                            activeKey={activeTab} 
                            onSelect={(k) => k && setActiveTab(k as string)} 
                            className="mb-3"
                        >
                        <Tab eventKey="details" title="Details">
                                <div className="mt-3">
                                    {data.latitude && data.longitude && (
                                        <div className="mb-3" style={{ border: '1px solid #ccc', borderRadius: '4px', overflow: 'hidden' }}>
                                            <iframe
                                                width="100%"
                                                height="300"
                                                frameBorder="0"
                                                style={{ border: 0 }}
                                                src={`https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${data.latitude},${data.longitude}&zoom=12`}
                                                allowFullScreen
                                            />
                                        </div>
                                    )}

                                    <div className="row mb-3">
                                        <div className="col-md-6">
                                            <h5>Basic Information</h5>
                                            <table className="table table-sm">
                                                <tbody>
                                                    <tr>
                                                        <td><strong>Server Timestamp:</strong></td>
                                                        <td>{formatDate(data.server_timestamp)}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>HTTP Method:</strong></td>
                                                        <td>{data.http_method || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>IP Address:</strong></td>
                                                        <td>{data.ip_address || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>IP Source:</strong></td>
                                                        <td>{data.ip_source || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Organization:</strong></td>
                                                        <td>{data.organization || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>ISP:</strong></td>
                                                        <td>{data.isp || NOT_AVAILABLE}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                        <div className="col-md-6">
                                            <h5>Client Information</h5>
                                            <table className="table table-sm">
                                                <tbody>
                                                    <tr>
                                                        <td><strong>OS:</strong></td>
                                                        <td>{data.os || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Browser:</strong></td>
                                                        <td>{data.browser || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Platform:</strong></td>
                                                        <td>{data.platform || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Locale:</strong></td>
                                                        <td>{data.locale || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Client Time:</strong></td>
                                                        <td>{formatDate(data.client_time)}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Client Timezone:</strong></td>
                                                        <td>{data.client_timezone || NOT_AVAILABLE}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-md-12">
                                            <h5>Location Information</h5>
                                            <table className="table table-sm">
                                                <tbody>
                                                    <tr>
                                                        <td><strong>Country:</strong></td>
                                                        <td>{data.country || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Region:</strong></td>
                                                        <td>{data.region || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>City:</strong></td>
                                                        <td>{data.city || NOT_AVAILABLE}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Latitude:</strong></td>
                                                        <td>{formatCoordinate(data.latitude)}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Longitude:</strong></td>
                                                        <td>{formatCoordinate(data.longitude)}</td>
                                                    </tr>
                                                    <tr>
                                                        <td><strong>Location Source:</strong></td>
                                                        <td>{data.location_source || NOT_AVAILABLE}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>

                                    {data.image_url && (
                                        <div className="mt-3">
                                            <h5>Image</h5>
                                            <img
                                                src={data.image_url}
                                                alt="Uploaded Image"
                                                style={{
                                                    maxWidth: '100%',
                                                    maxHeight: '500px',
                                                    border: '1px solid #ddd',
                                                    borderRadius: '4px',
                                                    padding: '5px',
                                                    backgroundColor: '#fff',
                                                }}
                                            />
                                        </div>
                                    )}
                                </div>
                        </Tab>

                        <Tab eventKey="warnings" title="Warnings">
                            <div className="mt-3">
                                {data && renderSecurityChecks(data)}
                                {data && renderIPAndHeaderConsistency(data)}
                                {data && renderBrowserAndClientChecks(data)}
                            </div>
                        </Tab>

                        {data._ip_data && (
                            <Tab eventKey="_ip_data" title="IP Data">
                                <div id="_ip_data-editor" style={{ height: '400px', marginTop: '1rem' }} />
                            </Tab>
                        )}

                        {data._user_agent_data && (
                            <Tab eventKey="_user_agent_data" title="User Agent Data">
                                <div id="_user_agent_data-editor" style={{ height: '400px', marginTop: '1rem' }} />
                            </Tab>
                        )}

                        {data._header_data && (
                            <Tab eventKey="_header_data" title="Header Data">
                                {data.image_url && (
                                    <div className="mb-3">
                                        <img
                                            src={data.image_url}
                                            alt="Uploaded Image"
                                            style={{
                                                maxWidth: '100%',
                                                maxHeight: '500px',
                                                border: '1px solid #ddd',
                                                borderRadius: '4px',
                                                padding: '5px',
                                                backgroundColor: '#fff',
                                            }}
                                        />
                                    </div>
                                )}
                                <div id="_header_data-editor" style={{ height: '400px' }} />
                            </Tab>
                        )}

                        {data._form_data && (
                            <Tab eventKey="_form_data" title="Form Data">
                                {data.image_url && (
                                    <div className="mb-3">
                                        <img
                                            src={data.image_url}
                                            alt="Uploaded Image"
                                            style={{
                                                maxWidth: '100%',
                                                maxHeight: '500px',
                                                border: '1px solid #ddd',
                                                borderRadius: '4px',
                                                padding: '5px',
                                                backgroundColor: '#fff',
                                            }}
                                        />
                                    </div>
                                )}
                                <div id="_form_data-editor" style={{ height: '400px' }} />
                            </Tab>
                        )}
                        </Tabs>
                    </div>
                )}
            </Modal.Body>
            <Modal.Footer>
                <button className="btn btn-secondary" onClick={onHide}>
                    Close
                </button>
            </Modal.Footer>
        </Modal>
    );
};

export default RequestDataModal;

