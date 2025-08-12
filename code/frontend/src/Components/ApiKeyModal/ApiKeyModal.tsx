import React, { useState, FormEvent, useEffect } from 'react';
import UserService from '../../Services/UserService';
import './ApiKeyModal.css';

interface ApiKeyModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const ApiKeyModal: React.FC<ApiKeyModalProps> = ({ isOpen, onClose }) => {
    const [apiKey, setApiKey] = useState('');
    const [apiKeyExists, setApiKeyExists] = useState(false);
    const [last4, setLast4] = useState<string | undefined>(undefined); // Novo estado para os 4 dígitos
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (isOpen) {
            setMessage('');
            setApiKey('');
            const checkStatus = async () => {
                setIsLoading(true);
                const status = await UserService.getApiKeyStatus();
                setApiKeyExists(status?.has_key || false);
                setLast4(status?.last4);
                setIsLoading(false);
            };
            checkStatus();
        }
    }, [isOpen]);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsLoading(true);
        setMessage('');
        try {
            const result = await UserService.setApiKey(apiKey);
            if (result) {
                setMessage("API key saved successfully!");
                const newStatus = await UserService.getApiKeyStatus();
                setApiKeyExists(newStatus?.has_key || false);
                setLast4(newStatus?.last4);
                setApiKey('');
            }
        } catch (err) {
            const errorMessage = `Failed to save API key. Please try again. ${err}`;
            setMessage(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="api-key-modal-overlay" onClick={isLoading ? undefined : onClose}>
            <div className="api-key-modal" onClick={(e) => e.stopPropagation()}>
                <h2>Manage API Key</h2>
                <p className="modal-description">
                    Your personal OpenRouter API key is used for all evaluations.
                    It is stored securely and never exposed in the browser.
                </p>

                <div className="api-key-status-display">
                    <strong>Current Key:</strong>
                    {isLoading ? (
                        <span>Checking...</span>
                    ) : apiKeyExists && last4 ? (
                        <span className="status-set">
                            •••• •••• •••• {last4}
                        </span>
                    ) : (
                        <span className="status-not-set">
                            Not Set
                        </span>
                    )}
                </div>

                <form onSubmit={handleSubmit} className="api-key-form">
                    <label htmlFor="apiKeyInput">
                        {apiKeyExists ? 'Enter a New Key to Update:' : 'Enter your API Key:'}
                    </label>
                    <input
                        id="apiKeyInput"
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-or-v1-..."
                        required
                        disabled={isLoading}
                    />
                    <button type="submit" className="save-api-key-button" disabled={isLoading || apiKey.length < 10}>
                        {isLoading ? 'Saving...' : 'Save API Key'}
                    </button>
                </form>

                {message && <p className="form-feedback-message">{message}</p>}
            </div>
        </div>
    );
};

export default ApiKeyModal;