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
        console.log(data);
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

    const handleDeleteClick = async (testId: string | number) => {
        const confirmed = window.confirm(`Are you sure you want to delete this test?`);
        if (confirmed) {
            try {
                setIsLoadingAction(true);
                const success = await TestService.deleteTestById(testId.toString());
                if (success) {
                    await fetchTests();
                } else {
                    alert("Failed to delete test. Please try again.");
                }
            } catch (error) {
                console.error("Error deleting test:", error);
                alert("An error occurred while deleting the test.");
            } finally {
                setIsLoadingAction(false);
            }
        }
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
                            <span className="test-time header">Execution Time</span>
                        </div>

                        {/* --- Data Rows --- */}
                        {tests.map((test) => (
                            <div
                                key={test.id}
                                className="test-card data-row"
                            >
                                <span className="test-id">{test.id}</span>
                                <span className="test-dataset" title={test.dataset.name}>
                                    {test.dataset.name}
                                </span>
                                <span className="test-model" title={test.llm_model.name || 'N/A'}>
                                    {test.llm_model.name}
                                </span>
                                <span className="test-correct-answers" title={test.correct_answers.toString() || 'N/A'}>
                                    {test.correct_answers.toString()}
                                </span>
                                <span className="test-accuracy" title={test.accuracy_percentage.toString() || 'N/A'}>
                                    {test.accuracy_percentage.toFixed(2) + '%'}
                                </span>
                                <span className="test-time">
                                    {Math.round((new Date(test.completed_at).getTime() - new Date(test.started_at).getTime()) / 1000) + 's'}
                                </span>
                                <div className="button-container">
                                    <button className="details-button" onClick={() => handleTestDetailsClick(test.id)}>
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>
                                    <button className="delete-button" onClick={() => handleDeleteClick(test.id)}>
                                        {isLoadingAction ? 'Deleting...' : 'Delete'}
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