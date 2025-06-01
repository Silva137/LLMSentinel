import React, { useEffect, useState } from "react";
import { Dataset } from "../../types/Dataset";
import DatasetService from "../../Services/DatasetService";
import "./CommunityDatasets.css";
import SearchIcon from "../../assets/searchIcon.svg?react";


const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return "N/A";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
};

const Community: React.FC = () => {
    const [publicDatasets, setPublicDatasets] = useState<Dataset[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const fetchPublicDatasets = async () => {
        setIsLoading(true);
        const data = await DatasetService.getPublicDatasets();
        //const data = await DatasetService.getAllDatasets();
        setPublicDatasets(data || []);
        setIsLoading(false);
    };

    const handleDownload = async (datasetId: number) => {
        try {
            //await DatasetService.downloadDataset(datasetId);
            alert("Dataset added to your collection!");
        } catch (error) {
            console.error("Download failed", error);
            alert("Failed to download dataset.");
        }
    };

    useEffect(() => {
        fetchPublicDatasets();
    }, []);

    return (
        <div className="page">
            <h1 className="page-title">Community Datasets</h1>

            <p className="pdatasets-available-text">
                {publicDatasets.length} public datasets available
            </p>

            <div className="pdatasets-grid">
                {isLoading ? (
                    <p className="loading-text">Loading public datasets...</p>
                ) : publicDatasets.length > 0 ? (
                    publicDatasets.map((dataset) => (
                        <div key={dataset.id} className="pdataset-card">
                            <h3 className="pdataset-name">{dataset.name}</h3>
                            <p className="pdataset-description">
                                {truncateText(dataset.description, 100)}
                            </p>
                            <p className="pdataset-owner">by {dataset.owner?.username ?? 'Default'}</p>
                            <div className="pdataset-footer">
                                <button
                                    className="download-button"
                                    onClick={() => handleDownload(dataset.id)}
                                >
                                    <SearchIcon className="download-icon" />
                                    Download
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="no-pdatasets-text">No public datasets found.</p>
                )}
            </div>
        </div>
    );
};

export default Community;
