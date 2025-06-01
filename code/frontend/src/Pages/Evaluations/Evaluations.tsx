import React, { useEffect, useState } from "react";
import TestService from "../../Services/TestService";
import "./Evaluations.css";
import { Test } from "../../types/Test";
import { useNavigate } from "react-router-dom";
import SearchIcon from "../../assets/searchIcon.svg?react";
import {Dataset} from "../../types/Dataset.ts";
import {LLMModel} from "../../types/LLMModel.ts";
import DatasetService from "../../Services/DatasetService.ts";
import LLMModelService from "../../Services/LLMModelService.ts";

const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

const Evaluations: React.FC = () => {
    const [tests, setTests] = useState<Test[]>([]);
    const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
    const [selectedDataset, setSelectedDataset] = useState<string>('');
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [models, setModels] = useState<LLMModel[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isLoadingAction, setIsLoadingAction] = useState<boolean>(false);
    const navigate = useNavigate();

    const fetchTests = async () => {
        setIsLoading(true);
        const data = await TestService.getAllTests();
        setTests(data || [])
        setIsLoading(false);
    };

    const fetchModalData = async () => {
        const fetchedDatasets = await DatasetService.getAllDatasets();
        const fetchedModels = await LLMModelService.getAllLLMModels();
        setDatasets(fetchedDatasets || []);
        setModels(fetchedModels|| []);
    };

    const handleTestDetailsClick = (testId: string | number) => {
        navigate(`/evaluations/${testId}/results`);
    };

    const handleDeleteClick = (testId: string | number) => {
        console.log(`Delete test with ID: ${testId}`);
        //todo
    };

    const handleCreateTest = async () => {
        if (!selectedDataset || !selectedModel) {
            alert("Please select both a dataset and a model.");
            return;
        }
        console.log(selectedModel + " " + selectedDataset);
        setIsLoadingAction(true);
        const newTest = await TestService.createTest(selectedDataset, selectedModel);
        if (newTest) {
            setShowCreateModal(false);
            setSelectedDataset("");
            setSelectedModel("");
            fetchTests();
        } else {
            console.error("Failed to create test");
        }

        setIsLoadingAction(false);
    };

    useEffect(() => {
        fetchTests();
    }, []);

    useEffect(() => {
        if (showCreateModal) {
            fetchModalData();
        }
    }, [showCreateModal]);

    return (
        <div className="page">
            <h1 className="page-title">Evaluations</h1>

            <button className="create-button" onClick={() => setShowCreateModal(true)}>
                Create new test
            </button>

            <div className="tests-list-container">
                {isLoading ? (
                    <p className="loading-text">Loading Tests...</p>
                ) : tests.length === 0 ? (
                    <p className="no-tests-text">No Tests available.</p>
                ) : (
                    <div className="tests-list">
                        {/* --- Header Row --- */}
                        <div className="test-card header-row">
                            <span className="test-id header">ID</span>
                            <span className="test-dataset header">Dataset</span>
                            <span className="test-llm-model header">LLM Model</span>
                            <span className="test-correct-answers header">Correct Answers</span>
                            <span className="test-accuracy header">Accuracy</span>
                        </div>

                        {/* --- Data Rows --- */}
                        {tests.map((test, index) => (
                            <div
                                key={test.id}
                                className="test-card data-row"
                            >
                                <span className="test-id">{index + 1}</span>
                                <span className="test-dataset" title={test.dataset.name}>
                                    {truncateText(test.dataset.name, 30)}
                                </span>
                                <span className="test-model" title={test.llm_model.name || 'N/A'}>
                                    {truncateText(test.llm_model.name, 20)}
                                </span>
                                <span className="test-correct-answers" title={test.correct_answers.toString() || 'N/A'}>
                                    {truncateText(test.correct_answers.toString(), 20)}
                                </span>
                                <span className="test-accuracy" title={test.accuracy_percentage.toString() || 'N/A'}>
                                    {truncateText(test.accuracy_percentage.toString(), 20)}
                                </span>
                                <div className="button-container">
                                    <button className="details-button" onClick={() => handleTestDetailsClick(test.id)}>
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>
                                    <button className="delete-button" onClick={() => handleDeleteClick(test.id)}>
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Create New Test</h2>

                        <label>Dataset:</label>
                        <select
                            value={selectedDataset}
                            onChange={(e) => setSelectedDataset(e.target.value)}
                        >
                            <option value="">Select Dataset</option>
                            {datasets.map((ds) => (
                                <option key={ds.id} value={ds.name}>{ds.name}</option>
                            ))}
                        </select>

                        <label>LLM Model:</label>
                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                        >
                            <option value="">Select Model</option>
                            {models.map((model) => (
                                <option key={model.model_id} value={model.name}>{model.name}</option>
                            ))}
                        </select>

                        <div className="modal-buttons">
                            <button onClick={() => setShowCreateModal(false)} className="cancel-button-modal">Cancel</button>
                            <button className="create-button-modal" onClick={handleCreateTest} disabled={!selectedDataset || !selectedModel}>
                                {isLoadingAction ? 'Running test...' : 'Create and run test'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Evaluations;