import { useState } from "react";
import "./UploadDatasetModal.css";
import DatasetService from "../../Services/DatasetService";

const UploadDatasetModal = ({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) => {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async () => {
        if (!name || !file) {
            setError("Dataset name and CSV file are required.");
            return;
        }
        setIsLoading(true);
        try {
            await DatasetService.uploadDataset(name, description, file);
            onSuccess()
            onClose();
        } catch (err) {
            console.error(err);
            setError("Failed to upload dataset.");
        }
        finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="upload-modal-overlay" onClick={isLoading ? undefined : onClose}>
            <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
                <h2>Upload New Dataset</h2>

                <div className="upload-modal-main-content">
                    {/* --- Left Column: Form --- */}
                    <div className="upload-form-section">
                        <label htmlFor="datasetNameInputModal">Name:</label>
                        <input
                            id="datasetNameInputModal"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            disabled={isLoading}
                        />

                        <label htmlFor="datasetDescInputModal">Description (optional):</label>
                        <textarea
                            id="datasetDescInputModal"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            rows={3}
                            disabled={isLoading}
                        />

                        <label htmlFor="datasetFileInputModal">CSV File:</label>
                        <input
                            id="datasetFileInputModal"
                            type="file"
                            accept=".csv"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            disabled={isLoading}
                        />
                        {file && <p className="file-name-display-modal">Selected: {file.name}</p>}
                        {error && <p className="upload-error-text-modal">{error}</p>}
                    </div>

                    {/* --- Right Column: Instructions --- */}
                    <div className="upload-instructions-section">
                        <h4>CSV File Requirements</h4>
                        <p>
                            The file must be semicolon (;) delimited, and  must contain the following exact column names:
                        </p>
                        <ul>
                            <li><strong>Question</strong></li>
                            <li><strong>Option A</strong></li>
                            <li><strong>Option B</strong></li>
                            <li><strong>Option C</strong></li>
                            <li><strong>Option D</strong></li>
                            <li><strong>Correct Answer</strong> (A, B, C, or D)</li>
                        </ul>

                        <p>The first two lines of your CSV file should look exactly like this:</p>
                        <pre className="csv-example-block">
                            <code>
                                sep=;<br />
                                Question;Option A;Option B;Option C;Option D;Correct Answer
                            </code>
                        </pre>
                    </div>
                </div>

                <div className="upload-modal-buttons">
                    <button onClick={onClose} className="upload-cancel-button" disabled={isLoading}>
                        Cancel
                    </button>
                    <button onClick={handleSubmit} className="upload-create-button" disabled={isLoading || !name.trim() || !file}>
                        {isLoading ? 'Uploading...' : 'Upload & Create'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UploadDatasetModal;
