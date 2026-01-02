import 'bootstrap-icons/font/bootstrap-icons.css';

interface ActionHandlerProps {
    handler: () => void;
}

export const ReactivateAction = ({ handler }: ActionHandlerProps) => {
    return (
        <i
            className="bi bi-arrow-clockwise text-success"
            style={{ cursor: 'pointer', fontSize: '1.2rem' }}
            onClick={handler}
            title="Reactivate"
        />
    );
};

export const DisableAction = ({ handler }: ActionHandlerProps) => {
    return (
        <i
            className="bi bi-x-circle text-warning"
            style={{ cursor: 'pointer', fontSize: '1.2rem' }}
            onClick={handler}
            title="Disable"
        />
    );
};

export const ViewAction = ({ handler }: ActionHandlerProps) => {
    return (
        <i
            className="bi bi-eye text-info"
            style={{ cursor: 'pointer', fontSize: '1.2rem' }}
            onClick={handler}
            title="View"
        />
    );
};

export const EditAction = ({ handler }: ActionHandlerProps) => {
    return (
        <i
            className="bi bi-pencil text-primary"
            style={{ cursor: 'pointer', fontSize: '1.2rem' }}
            onClick={handler}
            title="Edit"
        />
    );
};

export const DeleteAction = ({ handler }: ActionHandlerProps) => {
    return (
        <i
            className="bi bi-trash text-danger"
            style={{ cursor: 'pointer', fontSize: '1.2rem' }}
            onClick={handler}
            title="Delete"
        />
    );
};

