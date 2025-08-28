import React, { useEffect, useState } from "react";
import DatasetService from "../../Services/DatasetService.ts";
import "./Datasets.css";
import {Dataset} from "../../types/Dataset.ts";
import {useNavigate} from "react-router-dom";
import SearchIcon from "../../assets/searchIcon.svg?react";
import UploadDatasetModal from "../../Components/UploadDatasetModal/UploadDatasetModal.tsx";
import ConfirmationModal from "../../Components/ConfirmationModal/ConfirmationModal.tsx";
import TrashIcon from "../../assets/TrashIcon.svg?react";
import {Alert} from "@mui/material";




const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

const Datasets: React.FC = () => {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const navigate = useNavigate();
    const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
    const [isLoadingAction, setIsLoadingAction] = useState<boolean>(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);


    //-------- Confirmation Modal States --------
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false);
    const [datasetToDelete, setDatasetToDelete] = useState<Dataset | null>(null);



    const fetchDatasets = async () => {
        setIsLoading(true);
        const data = await DatasetService.getAllDatasets()
        console.log(data)
        setDatasets(data || []);
        setIsLoading(false);
    };

    const handleDatasetDetailsClick = (datasetId: string | number) => {
        navigate(`/datasets/${datasetId}/questions`);
    };

    const handleToggleShare = async (datasetId: string | number, makePublic: boolean) => {
        const action = makePublic ? "share" : "unshare";

        try {
            setIsLoadingAction(true);
            const success = await DatasetService.updateDatasetVisibility(datasetId.toString(), makePublic);
            if (success) {
                await fetchDatasets();
            } else {
                alert(`Failed to ${action} dataset. Please try again.`);
            }
        } catch (error) {
            console.error(`Error trying to ${action} dataset:`, error);
            alert(`An error occurred while trying to ${action} the dataset.`);
        } finally {
            setIsLoadingAction(false);
        }
    };


    const handleDeleteClick = (dataset: Dataset) => {
        setDatasetToDelete(dataset);
        setIsDeleteModalOpen(true);
    };


    const executeDelete = async () => {
        if (!datasetToDelete) return;


            setIsLoadingAction(true);
            const success = await DatasetService.deleteDatasetById(datasetToDelete.id.toString());
            if (success) {
                await fetchDatasets();
                setSuccessMessage("Dataset deleted successfully.");
            } else {
                alert("Failed to delete dataset. Please try again.");
            }

            setIsLoadingAction(false);
            setIsDeleteModalOpen(false);
            setDatasetToDelete(null);


    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    return (
        <div className="page">

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

            <h1 className="page-title">Datasets</h1>

            <button className="upload-button" onClick={() => setShowUploadModal(true)}>
                Upload Dataset
            </button>

            <div className="datasets-list-container">
                {isLoading ? (
                    <p className="loading-text">Loading datasets...</p>
                ) : datasets.length === 0 ? (
                    <p className="no-datasets-text">No datasets available.</p>
                ) : (
                    <div className="datasets-list">
                        {/* --- Header Row --- */}
                        <div className="dataset-card header-row">
                            <span className="dataset-id header">ID</span>
                            <span className="dataset-name header">Name</span>
                            <span className="dataset-description header">Description</span>
                            <span className="dataset-questions header">Questions</span>
                        </div>

                        {/* --- Data Rows --- */}
                        {datasets.map((dataset) => (
                            <div
                                key={dataset.id}
                                className="dataset-card data-row"
                            >
                                <span className="dataset-id">{dataset.id}</span>
                                <span className="dataset-name" title={dataset.name}>
                                    {truncateText(dataset.name, 30)}
                                </span>
                                <span className="dataset-description" title={dataset.description || 'N/A'}>
                                    {truncateText(dataset.description, 20)}
                                </span>
                                {/* --- change to display total questions --- */}
                                <span className="dataset-questions" title={dataset.total_questions.toString() || 'N/A'}>
                                    {truncateText(dataset.total_questions.toString(), 20)}
                                </span>
                                <div className="button-container">
                                    <button className="details-button" onClick={() => handleDatasetDetailsClick(dataset.id)}>
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>

                                    {dataset.owner && (
                                        <>
                                            <button
                                                className="share-button"
                                                onClick={() => handleToggleShare(dataset.id, !dataset.is_public)}
                                            >
                                                {dataset.is_public ? "Unshare" : "Share"}
                                            </button>
                                            <button className="delete-button" onClick={() => handleDeleteClick(dataset)} disabled={isLoadingAction}>
                                                <TrashIcon className="delete-icon" />
                                            </button>
                                        </>
                                    )}


                                </div>
                            </div>
                        ))}

                        <ConfirmationModal
                            isOpen={isDeleteModalOpen}
                            onCancel={() => setIsDeleteModalOpen(false)}
                            onConfirm={executeDelete}
                            isLoading={isLoadingAction}
                            title="Confirm Dataset Deletion"
                            message={
                                <>
                                    Are you sure you want to delete the dataset: <strong>{datasetToDelete?.name}</strong> ?
                                    <br />
                                    <br />
                                    <span style={{ color: '#e19d4e', fontWeight: 'bold' }}>
                            Warning: All associated tests and results will also be permanently removed.
                        </span>
                                </>
                            }
                            confirmButtonText="Delete Dataset"
                            loadingButtonText="Deleting..."
                        />
                    </div>
                )}
            </div>

            {showUploadModal && (
                <UploadDatasetModal
                    onClose={() => setShowUploadModal(false)}
                    onSuccess={() => {
                        fetchDatasets();
                        setShowUploadModal(false);
                    }}
                />
            )}
        </div>
    );
};

export default Datasets;