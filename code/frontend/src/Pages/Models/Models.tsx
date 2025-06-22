import React, { useEffect, useState } from "react";
import "./Models.css";
import {LLMModel} from "../../types/LLMModel.ts";
import LLMModelService from "../../Services/LLMModelService.ts";
import SearchIcon from "../../assets/searchIcon.svg?react";


const Models: React.FC = () => {
    const [models, setModels] = useState<LLMModel[]>([]);
    const [searchTerm, setSearchTerm] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

    const fetchModels = async () => {
        setIsLoading(true);
        const data = await LLMModelService.searchLLMModelsByName(searchTerm);
        setModels(data || []);
        setIsLoading(false);
    };

    useEffect(() => {
        fetchModels();
    }, []);

    const handleSearch = () => {
        fetchModels();
    };

    const toggleExpand = (index: number) => {
        setExpandedCards((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    return (
        <div className="page">
            <h1 className="page-title">Models</h1>

            {/* Search Bar */}
            <div className="search-container">
                <SearchIcon className="search-icon" onClick={handleSearch}/>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyDown={(e) => {if(e.key === "Enter") handleSearch()}}
                    placeholder="Search for models"
                    className="search-input"
                />
            </div>

            {/* Models Count */}
            <p className="models-available-text">{models.length} models available</p>

            {/* Models Grid */}
            <div className="models-grid">
                {isLoading ? (
                    <p className="loading-text">Loading models...</p>
                ) : models.length > 0 ? (
                    models.map((model, index) => (
                        <div
                            key={model.model_id}
                            className={`model-card ${expandedCards.has(index) ? 'expanded' : ''}`}
                            onClick={() => toggleExpand(index)}
                            style={{ cursor: 'pointer' }}
                        >
                            <h3 className="model-name">{model.name}</h3>
                            {model.description && (
                                <p className="model-description">
                                    {expandedCards.has(index) ? model.description : model.description.length > 100
                                        ? model.description.substring(0, 100) + '...'
                                        : model.description}
                                </p>
                            )}
                            <p className="model-provider">by {model.provider}</p>
                        </div>
                    ))
                ) : (
                    <p className="no-models-text">No models found matching your search.</p>
                )}
            </div>
        </div>
    );
};

export default Models;