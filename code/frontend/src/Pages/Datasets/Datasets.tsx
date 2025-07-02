import React, { useEffect, useState } from "react";
import DatasetService from "../../Services/DatasetService.ts";
import "./Datasets.css";
import {Dataset} from "../../types/Dataset.ts";
import {useNavigate} from "react-router-dom";
import SearchIcon from "../../assets/searchIcon.svg?react";
import UploadDatasetModal from "../../Components/UploadDatasetModal/UploadDatasetModal.tsx";


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
        const confirmed = window.confirm(`Are you sure you want to ${action} this dataset?`);
        if (!confirmed) return;

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

    const handleDeleteClick = async (datasetId: string | number) => {
        const confirmed = window.confirm(`Are you sure you want to delete this dataset? This action cannot be undone.`);
        if (confirmed) {
            try {
                setIsLoadingAction(true);
                const success = await DatasetService.deleteDatasetById(datasetId.toString());
                if (success) {
                    await fetchDatasets();
                } else {
                    alert("Failed to delete dataset. Please try again.");
                }
            } catch (error) {
                console.error("Error deleting dataset:", error);
                alert("An error occurred while deleting the dataset.");
            } finally {
                setIsLoadingAction(false);
            }
        }
    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    return (
        <div className="page">
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
                                            <button className="delete-button"
                                                    onClick={() => handleDeleteClick(dataset.id)}>
                                                {isLoadingAction ? 'Deleting...' : 'Delete'}
                                            </button>
                                        </>
                                    )}


                                </div>
                            </div>
                        ))}
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