import React, { useEffect, useState } from "react";
import { Dataset } from "../../types/Dataset";
import DatasetService from "../../Services/DatasetService";
import "./CommunityDatasets.css";
import SearchIcon from "../../assets/searchIcon.svg?react";
import {useAuth} from "../../Context/AuthContext.tsx";
import {Alert} from "@mui/material";
import {useNavigate} from "react-router-dom";

interface PageAlert {
    message: string;
    severity: 'success' | 'error' | 'info';
}

const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return "N/A";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
};

const Community: React.FC = () => {
    const [publicDatasets, setPublicDatasets] = useState<Dataset[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [pageAlert, setPageAlert] = useState<PageAlert | null>(null);
    const [searchTerm, setSearchTerm] = useState<string>("");
    const { user } = useAuth();
    const navigate = useNavigate();


    const fetchPublicDatasets = async () => {
        setIsLoading(true);
        const data = await DatasetService.searchPublicDatasetsByName(searchTerm);
        console.log(data);
        setPublicDatasets(data || []);
        setIsLoading(false);
    };

    const handleDownload = async (datasetId: number) => {
        const success = await DatasetService.cloneDataset(datasetId);
        if (success) {
            setPageAlert({ message: "Dataset added to your collection!", severity: 'success' });
        } else {
            setPageAlert({ message: "Download failed.", severity: 'error' });
            console.error("Download failed");
        }
    };

    const handleDatasetDetailsClick = (datasetId: number) => {
        navigate(`/datasets/${datasetId}/questions`);
    };

    const handleSearch = () => {
        fetchPublicDatasets();
    };


    useEffect(() => {
        fetchPublicDatasets();
    }, []);

    return (
        <div className="page">

            {pageAlert && (
                <div className="page-alert-container">
                    <Alert severity={pageAlert.severity} onClose={() => setPageAlert(null)} variant="filled">
                        {pageAlert.message}
                    </Alert>
                </div>
            )}

            <h1 className="page-title">Community Datasets</h1>

            {/* Search Bar */}
            <div className="search-container">
                <SearchIcon className="search-icon" onClick={handleSearch}/>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyDown={(e) => {if(e.key === "Enter") handleSearch()}}
                    placeholder="Search for datasets"
                    className="search-input"
                />
            </div>

            <p className="pdatasets-available-text">
                {publicDatasets.length} public datasets available
            </p>

            <div className="pdatasets-grid">
                {isLoading ? (
                    <p className="loading-text">Loading public datasets...</p>
                ) : publicDatasets.length > 0 ? (
                    publicDatasets.map((dataset) => (
                        <div key={dataset.id} className="pdataset-card">
                            <h3
                                className="pdataset-name"
                                onClick={() => handleDatasetDetailsClick(dataset.id)}
                                onKeyDown={(e) => e.key === 'Enter' && handleDatasetDetailsClick(dataset.id)}
                                role="button"
                                tabIndex={0}
                            >
                                {dataset.name}
                            </h3>
                            <p className="pdataset-description">
                                {truncateText(dataset.description, 100)}
                            </p>
                            <p className="pdataset-owner">by {dataset.owner.username || 'Default'}</p>
                            <div className="pdataset-footer">
                                <button
                                    className="download-button"
                                    onClick={() => handleDownload(dataset.id)}
                                    disabled={user?.username === dataset.owner.username}
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
