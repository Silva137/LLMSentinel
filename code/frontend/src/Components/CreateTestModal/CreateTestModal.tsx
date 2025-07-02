import React from "react";
import Select, {GroupBase, StylesConfig} from "react-select";
import { Dataset } from "../../types/Dataset.ts";
import { LLMModel } from "../../types/LLMModel.ts";
import "./CreateTestModal.css";

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
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <h2>Create New Test</h2>

                <label>Dataset:</label>
                <Select
                    className="react-select-container"
                    classNamePrefix="react-select"
                    options={datasets.map((ds) => ({
                        value: ds.name,
                        label: ds.name
                    }))}
                    value={selectedDataset ? { value: selectedDataset, label: selectedDataset } : null}
                    onChange={(selectedOption) => setSelectedDataset(selectedOption?.value || "")}
                    placeholder="Select Dataset..."
                    isSearchable
                    isClearable
                    styles={customSelectStyles}
                />

                <label>LLM Model:</label>
                <Select
                    className="react-select-container"
                    classNamePrefix="react-select"
                    options={models.map((model) => ({
                        value: model.name,
                        label: model.name
                    }))}
                    value={selectedModel ? { value: selectedModel, label: selectedModel } : null}
                    onChange={(selectedOption) => setSelectedModel(selectedOption?.value || "")}
                    placeholder="Select Model..."
                    isSearchable
                    isClearable
                    styles={customSelectStyles}
                />

                <div className="modal-buttons">
                    <button onClick={onCancel} className="cancel-button-modal">Cancel</button>
                    <button className="create-button-modal" onClick={onCreate} disabled={!selectedDataset || !selectedModel}>
                        {isLoading ? 'Running test...' : 'Create and run test'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CreateTestModal;

interface SelectOptionType {
    value: string;
    label: string;
}


// --- react-select custom styles (can be moved to a separate file) ---
const customSelectStyles: StylesConfig<SelectOptionType, false, GroupBase<SelectOptionType>> = {
    control: (provided, state) => ({
        ...provided,
        backgroundColor: '#1e2235', // Darker input background
        borderColor: state.isFocused ? '#6a6fbf' : '#363c58',
        boxShadow: state.isFocused ? '0 0 0 1px #6a6fbf' : 'none',
        borderRadius: '8px',
        minHeight: '40px', // Consistent height with other inputs
        color: '#e0e4ff',
        fontSize: '0.9rem',
        minWidth: '200px', // Fixed width for filter/sort dropdowns
        width: '400px',
        '&:hover': { borderColor: '#6a6fbf' },
    }),
    menu: (provided) => ({
        ...provided,
        backgroundColor: '#2f354c', // Dropdown menu background
        borderRadius: '8px',
        marginTop: '4px',
        zIndex: 10, // Ensure dropdown is above other elements
    }),
    option: (provided, state) => ({
        ...provided,
        backgroundColor: state.isSelected ? '#6a6fbf' : state.isFocused ? '#3b4262' : '#2f354c',
        color: state.isSelected ? 'white' : '#e0e4ff',
        padding: '10px 12px',
        cursor: 'pointer',
        fontSize: '0.9rem',
        '&:active': { backgroundColor: '#5564ae' },
    }),
    singleValue: (provided) => ({ ...provided, color: '#e0e4ff' }),
    placeholder: (provided) => ({ ...provided, color: '#a0a7d3' }),
    input: (provided) => ({ ...provided, color: '#e0e4ff' }),
    dropdownIndicator: (provided) => ({ ...provided, color: '#a0a7d3', '&:hover': { color: '#e0e4ff' }}),
    clearIndicator: (provided) => ({ ...provided, color: '#a0a7d3', '&:hover': { color: '#e0e4ff' }}),
    menuList: (provided) => ({
        ...provided,
        '&::-webkit-scrollbar': { width: '8px' },
        '&::-webkit-scrollbar-track': { background: '#2a2f45', borderRadius: '10px' },
        '&::-webkit-scrollbar-thumb': { backgroundColor: '#4a5175', borderRadius: '10px', border: '2px solid #2a2f45' },
        '&::-webkit-scrollbar-thumb:hover': { backgroundColor: '#5a67d8' },
        scrollbarWidth: 'thin',
        scrollbarColor: '#4a5175 #2a2f45',
    }),
};
