import React, { useEffect, useState } from "react";
import TestService from "../../Services/TestService";
import './Evaluations.css';
import '../../Components/CreateTestModal/CreateTestModal.css';
import { Test } from "../../types/Test";
import { useNavigate } from "react-router-dom";
import SearchIcon from "../../assets/searchIcon.svg?react";
import TrashIcon from "../../assets/TrashIcon.svg?react";
import { Dataset } from "../../types/Dataset.ts";
import { LLMModel } from "../../types/LLMModel.ts";
import DatasetService from "../../Services/DatasetService.ts";
import LLMModelService, { TestedModels } from "../../Services/LLMModelService.ts";
import CreateTestModal from "../../Components/CreateTestModal/CreateTestModal.tsx";
import Select, {GroupBase, SingleValue } from 'react-select';
import ResultsService, {SelectableDataset} from "../../Services/ResultsService.ts";
import {customSelectStyles, SelectOptionType} from "../../Styles/CustomSelectStyles.ts";
import {CreateTestErrors} from "../../types/errors.ts";
import axios from "axios";
import {Alert} from "@mui/material";
import ConfirmationModal from "../../Components/ConfirmationModal/ConfirmationModal.tsx";


const Evaluations: React.FC = () => {
    const [tests, setTests] = useState<Test[]>([]);
    const [showCreateModal, setShowCreateModal] = useState<boolean>(false);

    // --- States for CreateTestModal ---
    const [modalDatasets, setModalDatasets] = useState<Dataset[]>([]);
    const [modalModels, setModalModels] = useState<LLMModel[]>([]);
    const [selectedDatasetForCreation, setSelectedDatasetForCreation] = useState<string>('');
    const [selectedModelForCreation, setSelectedModelForCreation] = useState<string>('');
    // ---------------------------------------------------

    const [filterDatasetName, setFilterDatasetName] = useState<string>('');
    const [filterModelName, setFilterModelName] = useState<string>('');
    const [sortCriteria, setSortCriteria] = useState<string>('id_desc');

    // --- States to populate filter dropdowns ---
    const [availableFilterDatasets, setAvailableFilterDatasets] = useState<SelectableDataset[]>([]);
    const [availableFilterModels, setAvailableFilterModels] = useState<TestedModels[]>([]);
    // -----------------------------------------

    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isLoadingAction, setIsLoadingAction] = useState<boolean>(false);
    const [isRunningTest, setIsRunningTest] = useState<boolean>(false);
    const [createError, setCreateError] = useState<CreateTestErrors | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);


    //--------------delete modal confirmation -------------
    const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);
    const [testToDelete, setTestToDelete] = useState<Test | null>(null);


    const navigate = useNavigate();

    // Fetch tests based on current filters and sort criteria from backend
    const fetchTests = async () => {
        setIsLoading(true);
        try {
            const data = await TestService.getAllTests(
                filterDatasetName,
                filterModelName,
                sortCriteria
            );
            setTests(data || []);
        } catch (error) {
            console.error("Error fetching tests:", error);
            setTests([]);
        } finally {
            setIsLoading(false);
        }
    };

    // Fetch data for create modal dropdowns (datasets & all models)
    const fetchModalData = async () => {
        setIsLoadingAction(true);
        try {
            const [fetchedDatasets, fetchedModels] = await Promise.all([
                DatasetService.getAllDatasetsFromUser(),
                LLMModelService.getAllLLMModels()
            ]);
            setModalDatasets(fetchedDatasets || []);
            setModalModels(fetchedModels || []);
        } catch (error) {
            console.error("Error fetching modal data:", error);
        } finally {
            setIsLoadingAction(false);
        }
    };

    // Fetch data for filter dropdowns (only tested datasets/models)
    const fetchFilterOptions = async () => {
        try {
            const [testedDs, testedMls] = await Promise.all([
                ResultsService.getAvailableDatasetsForModels([]), // New service method needed
                LLMModelService.getTestedModels()    // You have this
            ]);
            setAvailableFilterDatasets(testedDs || []);
            setAvailableFilterModels(testedMls || []);
        } catch (error) {
            console.error("Error fetching filter options:", error);
        }
    };


    useEffect(() => {
        fetchFilterOptions();
    }, []);

    useEffect(() => {
        fetchTests();
    }, [filterDatasetName, filterModelName, sortCriteria]);

    useEffect(() => {
        if (showCreateModal) {
            fetchModalData();
        }
    }, [showCreateModal]);


    const handleTestDetailsClick = (testId: string | number) => {
        navigate(`/evaluations/${testId}/results`);
    };

    const modalClose = () => {
        setShowCreateModal(false);
        setSelectedModelForCreation('');
        setSelectedDatasetForCreation('');
    }


    const handleDeleteClick = (test: Test) => {
        setTestToDelete(test);
        setShowDeleteModal(true);
    };


    const executeDelete = async () => {
        if (!testToDelete) return;

        setIsLoadingAction(true);
        const success = await TestService.deleteTestById(testToDelete.id.toString());
        if (success) {
            await fetchTests();
            setSuccessMessage("Test deleted successfully.");
        } else {
            alert("Failed to delete test. Please try again.");
        }

        setIsLoadingAction(false);
        setShowDeleteModal(false);
        setTestToDelete(null);
    };

    const handleCreateTest = async () => {
        setIsRunningTest(true);
        setCreateError(null)

        try{
            const newTest = await TestService.createTest(selectedDatasetForCreation, selectedModelForCreation);
            setSuccessMessage("Test created successfully.");
            console.log(newTest);
            fetchTests();
            fetchFilterOptions();

        } catch (error){

            console.error("Failed to create test:", error);
            if (axios.isAxiosError(error) && error.response) {
                const creationErrors: CreateTestErrors = error.response.data;
                setCreateError(creationErrors);
            }
            else {
                setCreateError({ error: "An unexpected error occurred. Please try again." });
            }

        } finally {
            setShowCreateModal(false);
            setSelectedDatasetForCreation("");
            setSelectedModelForCreation("");
            setIsRunningTest(false);
        }
    };

    // Options for the consolidated sort dropdown
    const sortOptions: SelectOptionType[] = [
        { value: 'accuracy_desc', label: 'Best Accuracy' },
        { value: 'accuracy_asc', label: 'Worst Accuracy' },
        { value: 'time_asc', label: 'Best Time' },
        { value: 'time_desc', label: 'Worst Time' },
        { value: 'id_desc', label: 'Recent '},
        { value: 'id_asc', label: 'Oldest'}
    ];


    return (
        <div className="page evaluations-page">

            {createError && (
                <Alert
                    className="custom-error-alert"
                    variant="filled"
                    severity="error"
                    onClose={() => setCreateError(null)}
                >
                    {createError.error || "An error occurred while creating the test."}
                </Alert>
            )}

            {successMessage && (
                <Alert
                    className="custom-success-alert"
                    variant="filled"
                    severity="success"
                    onClose={() => setSuccessMessage(null)}
                >
                    {successMessage}
                </Alert>
            )}

            <div className="evaluations-header">
                <h1 className="page-title">Evaluations</h1>
                <button className="create-button" onClick={() => setShowCreateModal(true)} disabled={isLoadingAction}>
                    Create new test
                </button>
            </div>

            <div className="evaluations-controls">
                <div className="control-group">
                    <label htmlFor="filter-dataset-eval">Dataset:</label>
                    <Select<SelectOptionType, false, GroupBase<SelectOptionType>>
                        id="filter-dataset-eval"
                        styles={customSelectStyles}
                        options={[{ value: '', label: 'All Datasets' }, ...availableFilterDatasets.map(ds => ({ value: ds.name, label: ds.name }))]}
                        value={filterDatasetName ? { value: filterDatasetName, label: filterDatasetName } : { value: '', label: 'All Datasets' }}
                        onChange={(option: SingleValue<SelectOptionType>) => setFilterDatasetName(option ? option.value : '')}
                        placeholder="Filter by Dataset..."
                        isClearable
                        isSearchable
                    />
                </div>
                <div className="control-group">
                    <label htmlFor="filter-model-eval">Model:</label>
                    <Select<SelectOptionType, false, GroupBase<SelectOptionType>>
                        id="filter-model-eval"
                        styles={customSelectStyles}
                        options={[{ value: '', label: 'All Models' }, ...availableFilterModels.map(model => ({ value: model.name, label: model.name }))]}
                        value={filterModelName ? { value: filterModelName, label: filterModelName } : { value: '', label: 'All Models' }}
                        onChange={(option: SingleValue<SelectOptionType>) => setFilterModelName(option ? option.value : '')}
                        placeholder="Filter by Model..."
                        isClearable
                        isSearchable
                    />
                </div>
                <div className="control-group">
                    <label htmlFor="sort-criteria-eval">Sort by:</label>
                    <Select<SelectOptionType, false, GroupBase<SelectOptionType>>
                        id="sort-criteria-eval"
                        styles={customSelectStyles}
                        options={sortOptions}
                        value={sortOptions.find(opt => opt.value === sortCriteria)}
                        onChange={(option: SingleValue<SelectOptionType>) => setSortCriteria(option ? option.value : 'id_desc')}
                        defaultValue={sortOptions.find(opt => opt.value === 'id_desc')}
                    />
                </div>
            </div>

            <div className="tests-list-container">
                {isLoading && tests.length === 0 ? (
                    <p className="loading-text">Loading Tests...</p>
                ) : !isLoading && tests.length === 0 ? (
                    <p className="no-tests-text">
                        {filterDatasetName || filterModelName ? "No tests match your current filters." : "No Tests available."}
                    </p>
                ) : (
                    <div className="tests-list">
                        <div className="test-card header-row">
                            <span className="test-id header">ID</span>
                            <span className="test-dataset header">Dataset</span>
                            <span className="test-llm-model header">LLM Model</span>
                            <span className="test-correct-answers header">Correct Ans.</span>
                            <span className="test-accuracy header">Accuracy</span>
                            <span className="test-CI header">95% CI (±)</span>
                            <span className="test-time header">Execution Time</span>
                            <span className="test-actions header">Actions</span>
                        </div>
                        {tests.map((test) => (
                            <div key={test.id} className="test-card data-row">
                                <span className="test-id">{test.id}</span>
                                <span className="test-dataset" title={test.dataset.name}>
                                    {test.dataset.name}
                                </span>
                                <span className="test-llm-model" title={test.llm_model.name || 'N/A'}>
                                    {test.llm_model.name}
                                </span>
                                <span className="test-correct-answers">
                                    {`${test.correct_answers}/${test.dataset.total_questions}`}
                                </span>
                                <span className="test-accuracy">
                                    {test.accuracy_percentage !== null ? test.accuracy_percentage.toFixed(2) + '%' : 'N/A'}
                                </span>
                                <span className="test-CI">
                                    {`+${(test.confidence_interval_high - test.accuracy_percentage).toFixed(1)} / -${(test.accuracy_percentage - test.confidence_interval_low).toFixed(1)}`}
                                </span>
                                <span className="test-time">
                                    {test.completed_at && test.started_at
                                        ? Math.round((new Date(test.completed_at).getTime() - new Date(test.started_at).getTime()) / 1000) + 's'
                                        : 'N/A'}
                                </span>
                                <div className="button-container test-actions">
                                    <button className="details-button" onClick={() => handleTestDetailsClick(test.id)}>
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>
                                    <button className="delete-button" onClick={() => handleDeleteClick(test)} disabled={isLoadingAction}>
                                        <TrashIcon className="delete-icon" />
                                    </button>
                                </div>
                            </div>
                        ))}

                        <ConfirmationModal
                            isOpen={showDeleteModal}
                            onCancel={() => setShowDeleteModal(false)}
                            onConfirm={executeDelete}
                            isLoading={isLoadingAction}
                            title="Confirm Test Deletion"
                            message={
                                <>
                                    Are you sure you want to permanently delete the test for model
                                    <strong> {testToDelete?.llm_model.name} </strong>
                                    on dataset <strong>{testToDelete?.dataset.name}</strong> (ID: {testToDelete?.id}) ?
                                </>
                            }
                            confirmButtonText="Delete Test"
                            loadingButtonText="Deleting..."
                        />
                    </div>
                )}
            </div>

            {showCreateModal && (
                <CreateTestModal
                    datasets={modalDatasets}
                    models={modalModels}
                    selectedDataset={selectedDatasetForCreation}
                    setSelectedDataset={setSelectedDatasetForCreation}
                    selectedModel={selectedModelForCreation}
                    setSelectedModel={setSelectedModelForCreation}
                    onCancel={modalClose}
                    onCreate={handleCreateTest}
                    isLoading={isRunningTest}
                />
            )}
        </div>
    );
};

export default Evaluations;




