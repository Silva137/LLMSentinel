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
                        {datasets.map((dataset, index) => (
                            <div
                                key={dataset.id}
                                className="dataset-card data-row"
                            >
                                <span className="dataset-id">{index + 1}</span> {/* Displaying index + 1 */}
                                <span className="dataset-name" title={dataset.name}>
                                    {truncateText(dataset.name, 30)}
                                </span>
                                <span className="dataset-description" title={dataset.description || 'N/A'}>
                                    {truncateText(dataset.description, 20)}
                                </span>
                                {/* --- change to display total questions --- */}
                                <span className="dataset-questions" title={dataset.description || 'N/A'}>
                                    {truncateText(dataset.description, 20)}
                                </span>
                                <div className="button-container">
                                    <button className="details-button" onClick={() => handleDatasetDetailsClick(dataset.id)}>
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>
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