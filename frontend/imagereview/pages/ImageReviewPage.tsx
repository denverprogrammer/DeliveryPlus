import { useState } from 'react';
import { Form, Button, Alert, Card, Spinner } from 'react-bootstrap';
import { uploadImage } from '../services/api';

interface UploadResponse {
    status: string;
    detail?: string;
    error?: string;
}

function ImageReviewPage() {
    const [token, setToken] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [response, setResponse] = useState<UploadResponse | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                setResponse({ status: 'error', error: 'Please select an image file' });
                return;
            }
            
            setSelectedFile(file);
            setResponse(null);
            
            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!token) {
            setResponse({ status: 'error', error: 'Token is required' });
            return;
        }
        
        if (!selectedFile) {
            setResponse({ status: 'error', error: 'Please select an image file' });
            return;
        }

        setUploading(true);
        setResponse(null);

        try {
            const result = await uploadImage(token, selectedFile);
            setResponse(result);
            
            // Reset form on success
            if (result.status === 'success') {
                setToken('');
                setSelectedFile(null);
                setPreview(null);
                const fileInput = document.getElementById('imageFile') as HTMLInputElement;
                if (fileInput) {
                    fileInput.value = '';
                }
            }
        } catch (error) {
            setResponse({ 
                status: 'error', 
                error: error instanceof Error ? error.message : 'Failed to upload image' 
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="row justify-content-center">
            <div className="col-md-8 col-lg-6">
                <Card>
                    <Card.Header>
                        <h2 className="mb-0">Upload Image with EXIF Data</h2>
                    </Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Token</Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Enter token"
                                    value={token}
                                    onChange={(e) => setToken(e.target.value)}
                                    required
                                    disabled={uploading}
                                />
                                <Form.Text className="text-muted">
                                    Enter the tracking token to associate with this image
                                </Form.Text>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label>Image File</Form.Label>
                                <Form.Control
                                    id="imageFile"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    disabled={uploading}
                                    required
                                />
                                <Form.Text className="text-muted">
                                    Select an image file (JPEG, PNG, etc.)
                                </Form.Text>
                            </Form.Group>

                            {preview && (
                                <div className="mb-3">
                                    <p className="mb-2">Preview:</p>
                                    <img 
                                        src={preview} 
                                        alt="Preview" 
                                        style={{ maxWidth: '100%', maxHeight: '300px', objectFit: 'contain' }}
                                    />
                                </div>
                            )}

                            {response && (
                                <Alert 
                                    variant={response.status === 'success' ? 'success' : 'danger'}
                                    className="mb-3"
                                >
                                    {response.status === 'success' ? (
                                        <div>
                                            <strong>Success!</strong> {response.detail || 'Image uploaded successfully'}
                                        </div>
                                    ) : (
                                        <div>
                                            <strong>Error:</strong> {response.error || response.detail || 'Failed to upload image'}
                                        </div>
                                    )}
                                </Alert>
                            )}

                            <Button 
                                variant="primary" 
                                type="submit" 
                                disabled={uploading || !token || !selectedFile}
                                className="w-100"
                            >
                                {uploading ? (
                                    <>
                                        <Spinner
                                            as="span"
                                            animation="border"
                                            size="sm"
                                            role="status"
                                            aria-hidden="true"
                                            className="me-2"
                                        />
                                        Uploading...
                                    </>
                                ) : (
                                    'Upload Image'
                                )}
                            </Button>
                        </Form>
                    </Card.Body>
                </Card>
            </div>
        </div>
    );
}

export default ImageReviewPage;

