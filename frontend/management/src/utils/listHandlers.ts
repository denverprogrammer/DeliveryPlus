import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';

interface UseListHandlersOptions<T extends { id: number }> {
    baseRoute: string;
    onDelete: (id: number) => Promise<void>;
    onDeleteSuccess: () => Promise<void>;
    deleteConfirmMessage: string;
}

export const useActionHandlers = <T extends { id: number }>({
    baseRoute,
    onDelete,
    onDeleteSuccess,
    deleteConfirmMessage,
}: UseListHandlersOptions<T>) => {
    const navigate = useNavigate();

    const handleView = useCallback((item: T) => {
        navigate(`${baseRoute}/${item.id}`);
    }, [navigate, baseRoute]);

    const handleEdit = useCallback((item: T) => {
        navigate(`${baseRoute}/${item.id}/edit`);
    }, [navigate, baseRoute]);

    const handleDelete = useCallback(async (item: T) => {
        if (!window.confirm(deleteConfirmMessage)) {
            return;
        }
        try {
            await onDelete(item.id);
            await onDeleteSuccess();
        } catch (err) {
            // Error handling is done in the component's error state
            throw err;
        }
    }, [onDelete, onDeleteSuccess, deleteConfirmMessage]);

    return {
        handleView,
        handleEdit,
        handleDelete,
    };
};

