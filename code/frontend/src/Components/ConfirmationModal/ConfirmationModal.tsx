import React from 'react';
import './ConfirmationModal.css'; // Vamos usar um CSS com o mesmo nome

interface ConfirmationModalProps {
    isOpen: boolean;
    onCancel: () => void;
    onConfirm: () => void;
    isLoading: boolean;
    title: string;
    message: React.ReactNode;
    confirmButtonText?: string;
    cancelButtonText?: string;
    loadingButtonText?: string;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
     isOpen,
     onCancel,
     onConfirm,
     isLoading,
     title,
     message,
     confirmButtonText = 'Confirm',
     cancelButtonText = 'Cancel',
     loadingButtonText = 'Processing...'
 }) => {
    if (!isOpen) {
        return null;
    }

    return (
        <div className="modal-overlay" onClick={isLoading ? undefined : onCancel}>
            <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
                <h2 className="confirm-modal-title">{title}</h2>
                <p className="confirm-modal-text">{message}</p>
                <div className="confirm-modal-buttons">
                    <button
                        className="modal-button cancel"
                        onClick={onCancel}
                        disabled={isLoading}
                    >
                        {cancelButtonText}
                    </button>
                    <button
                        className="modal-button confirm-action" // Classe mais genérica
                        onClick={onConfirm}
                        disabled={isLoading}
                    >
                        {isLoading ? loadingButtonText : confirmButtonText}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;