import React, { useState } from "react";
import "./UploadDatasetModal.css";
import DatasetService from "../../Services/DatasetService";

const UploadDatasetModal = ({ onClose, onSuccess }: { onClose: () => void, onSuccess: () => void }) => {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [error, setError] = useState("");

    const handleSubmit = async () => {
        if (!name || !file) {
            setError("Name and file are required.");
            return;
        }
        try {
            await DatasetService.uploadDataset(name, description, file);
            alert("Dataset uploaded successfully!");
            onSuccess()
            onClose();
        } catch (err) {
            console.error(err);
            setError("Failed to upload dataset.");
        }
    };

    return (
        <div className="upload-modal-overlay" onClick={onClose}>
            <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
                <h2>Upload Dataset</h2>
                <label>Name:</label>
                <input value={name} onChange={(e) => setName(e.target.value)} />

                <label>Description (optional):</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} />

                <label>CSV File:</label>
                <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />

                {error && <p className="error-text">{error}</p>}

                <div className="upload-modal-buttons">
                    <button onClick={onClose} className="upload-cancel-button">Cancel</button>
                    <button onClick={handleSubmit} className="upload-create-button">Upload</button>
                </div>
            </div>
        </div>
    );
};

export default UploadDatasetModal;
