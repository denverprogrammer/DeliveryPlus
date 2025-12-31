import React from 'react';
import { Form, Pagination } from 'react-bootstrap';

interface PaginationInfo {
    page: number;
    page_size: number;
    total_pages: number;
    count: number;
}

interface PaginationControlsProps {
    pagination: PaginationInfo;
    pageSize: number;
    onPageChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
    pageSizeOptions?: number[];
}

const PaginationControls: React.FC<PaginationControlsProps> = ({
    pagination,
    pageSize,
    onPageChange,
    onPageSizeChange,
    pageSizeOptions = [5, 10, 20, 50, 100],
}) => {
    const renderPageNumbers = () => {
        const maxVisible = 5;
        const pages: number[] = [];

        if (pagination.total_pages <= maxVisible) {
            // Show all pages if total is less than max visible
            for (let i = 1; i <= pagination.total_pages; i++) {
                pages.push(i);
            }
        } else if (pagination.page <= 3) {
            // Show first 5 pages
            for (let i = 1; i <= maxVisible; i++) {
                pages.push(i);
            }
        } else if (pagination.page >= pagination.total_pages - 2) {
            // Show last 5 pages
            for (let i = pagination.total_pages - 4; i <= pagination.total_pages; i++) {
                pages.push(i);
            }
        } else {
            // Show 2 pages before and after current
            for (let i = pagination.page - 2; i <= pagination.page + 2; i++) {
                pages.push(i);
            }
        }

        return pages.map((pageNum) => (
            <Pagination.Item
                key={pageNum}
                active={pageNum === pagination.page}
                onClick={() => onPageChange(pageNum)}
            >
                {pageNum}
            </Pagination.Item>
        ));
    };

    return (
        <div className="d-flex justify-content-between align-items-center mt-3">
            <Form.Group className="d-flex align-items-center mb-0">
                <Form.Label className="me-2 mb-0">Page Size:</Form.Label>
                <Form.Select
                    size="sm"
                    style={{ width: 'auto' }}
                    value={pageSize}
                    onChange={(e) => onPageSizeChange(parseInt(e.target.value, 10))}
                >
                    {pageSizeOptions.map((size) => (
                        <option key={size} value={size}>
                            {size}
                        </option>
                    ))}
                </Form.Select>
            </Form.Group>

            {pagination.total_pages > 1 && (
                <Pagination className="mb-0">
                    <Pagination.First
                        disabled={pagination.page === 1}
                        onClick={() => onPageChange(1)}
                    />
                    <Pagination.Prev
                        disabled={pagination.page === 1}
                        onClick={() => onPageChange(pagination.page - 1)}
                    />
                    {renderPageNumbers()}
                    <Pagination.Next
                        disabled={pagination.page === pagination.total_pages}
                        onClick={() => onPageChange(pagination.page + 1)}
                    />
                    <Pagination.Last
                        disabled={pagination.page === pagination.total_pages}
                        onClick={() => onPageChange(pagination.total_pages)}
                    />
                </Pagination>
            )}
        </div>
    );
};

export default PaginationControls;

