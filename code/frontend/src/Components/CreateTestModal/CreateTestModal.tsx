import React from "react";
import Select from "react-select";
import { Dataset } from "../../types/Dataset.ts";
import { LLMModel } from "../../types/LLMModel.ts";
import "./CreateTestModal.css";
import {customSelectStylesModal} from "../../Styles/CustomSelectStyles.ts";

interface CreateTestModalProps {
    datasets: Dataset[];
    models: LLMModel[];
    selectedDataset: string;
    selectedModel: string;
    setSelectedDataset: (value: string) => void;
    setSelectedModel: (value: string) => void;
    onCancel: () => void;
    onCreate: () => void;
    isLoading: boolean;
}

const CreateTestModal: React.FC<CreateTestModalProps> = ({
         datasets,
         models,
         selectedDataset,
         selectedModel,
         setSelectedDataset,
         setSelectedModel,
         onCancel,
         onCreate,
         isLoading
     }) => {

    const handleOverlayClick = () => {
        if (!isLoading) {
            onCancel();
        }
    };

    return (
        <div className={`modal-overlay ${isLoading ? "is-loading" : ""}`} onClick={handleOverlayClick}>
            <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-busy={isLoading}>
                {isLoading ? (
                    <div className="modal-loading">
                        <div className="modal-spinner" aria-label="Loading" />
                        <h2>Running test…</h2>
                        <p className="modal-loading-text">Please wait, this can take a few minutes…</p>
                    </div>
                ) : (
                    <>
                        <h2>Create New Test</h2>

                        <label>Dataset:</label>
                        <Select
                            className="react-select-container"
                            classNamePrefix="react-select"
                            options={datasets.map((ds) => ({ value: ds.name, label: ds.name }))}
                            value={selectedDataset ? { value: selectedDataset, label: selectedDataset } : null}
                            onChange={(opt) => setSelectedDataset(opt?.value || "")}
                            placeholder="Select Dataset..."
                            isSearchable
                            isClearable
                            styles={customSelectStylesModal}
                        />

                        <label>LLM Model:</label>
                        <Select
                            className="react-select-container"
                            classNamePrefix="react-select"
                            options={models.map((m) => ({ value: m.name, label: m.name }))}
                            value={selectedModel ? { value: selectedModel, label: selectedModel } : null}
                            onChange={(opt) => setSelectedModel(opt?.value || "")}
                            placeholder="Select Model..."
                            isSearchable
                            isClearable
                            styles={customSelectStylesModal}
                        />

                        <div className="modal-buttons">
                            <button onClick={onCancel} className="cancel-button-modal">Cancel</button>
                            <button
                                className="create-button-modal"
                                onClick={onCreate}
                                disabled={!selectedDataset || !selectedModel}
                            >
                                Create and run test
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default CreateTestModal;