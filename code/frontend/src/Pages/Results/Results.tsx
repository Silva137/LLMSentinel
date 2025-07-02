// src/Pages/Results/Results.tsx
import React, { useEffect, useState, useMemo } from 'react';
import ResultsService, { SelectableModel, SelectableDataset, ModelPerformanceData } from '../../Services/ResultsService';
import CombinedPerformanceBarChart from '../../Components/PerformaceChart.tsx';
import './Results.css';

const MAX_SELECTED_MODELS = 8;

const Results: React.FC = () => {
    const [testedModels, setTestedModels] = useState<SelectableModel[]>([]);
    const [selectedModelIds, setSelectedModelIds] = useState<Set<string>>(new Set());
    const [availableDatasets, setAvailableDatasets] = useState<SelectableDataset[]>([]);
    const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
    const [rawPerformanceData, setRawPerformanceData] = useState<ModelPerformanceData[]>([]);
    const [isLoadingModels, setIsLoadingModels] = useState<boolean>(true);
    const [isLoadingDatasets, setIsLoadingDatasets] = useState<boolean>(false);
    const [isLoadingChartData, setIsLoadingChartData] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);


    useEffect(() => {
        const fetchModels = async () => {
            setIsLoadingModels(true);
            try {
                const models = await ResultsService.getTestedModels();
                setTestedModels(models || []);
            } catch (err) {
                console.error("Failed to fetch tested models:", err);
                setError("Could not load model list.");
            } finally {
                setIsLoadingModels(false);
            }
        };
        fetchModels();
    }, []);

    useEffect(() => {
        if (selectedModelIds.size > 0) {
            const fetchDatasets = async () => {
                setIsLoadingDatasets(true);
                setError(null);
                try {
                    const datasets = await ResultsService.getAvailableDatasetsForModels(Array.from(selectedModelIds));
                    setAvailableDatasets(datasets || []);
                    if (datasets && datasets.length > 0) {
                        if (!selectedDatasetId || !datasets.find(d => d.id === selectedDatasetId)) {
                            setSelectedDatasetId(datasets[0].id);
                        }
                    } else {
                        setSelectedDatasetId('');
                        setRawPerformanceData([]);
                    }
                } catch (err) {
                    console.error("Failed to fetch available datasets:", err);
                    setError("Could not load dataset list for selected models.");
                    setAvailableDatasets([]);
                    setSelectedDatasetId('');
                    setRawPerformanceData([]);
                } finally {
                    setIsLoadingDatasets(false);
                }
            };
            fetchDatasets();
        } else {
            setAvailableDatasets([]);
            setSelectedDatasetId('');
            setRawPerformanceData([]);
        }
    }, [selectedModelIds]);

    useEffect(() => {
        if (selectedModelIds.size > 0 && selectedDatasetId) {
            const fetchPerformanceData = async () => {
                setIsLoadingChartData(true);
                setError(null);
                try {
                    const data = await ResultsService.getModelsPerformanceDataOnDataset(
                        Array.from(selectedModelIds),
                        selectedDatasetId
                    );
                    setRawPerformanceData(data || []);
                    console.log("Fetched performance data:", data);
                } catch (err) {
                    console.error("Failed to fetch performance data:", err);
                    setError("Could not load performance data for the selected dataset.");
                    setRawPerformanceData([]);
                } finally {
                    setIsLoadingChartData(false);
                }
            };
            fetchPerformanceData();
        } else if (selectedModelIds.size === 0 || !selectedDatasetId) {
            setRawPerformanceData([]);
            setIsLoadingChartData(false);
        }
    }, [selectedModelIds, selectedDatasetId]);


    const handleModelSelectionChange = (modelId: string) => {
        setSelectedModelIds(prevSelected => {
            const newSelected = new Set(prevSelected);
            if (newSelected.has(modelId)) {
                newSelected.delete(modelId);
            } else {
                if (newSelected.size < MAX_SELECTED_MODELS) {
                    newSelected.add(modelId);
                } else {
                    alert(`You can select a maximum of ${MAX_SELECTED_MODELS} models.`);
                }
            }
            return newSelected;
        });
    };


    const processedChartData = useMemo((): ModelPerformanceData[] => {
        return rawPerformanceData.filter(item =>
            item.modelName !== undefined &&
            item.accuracyPercentage !== null && item.accuracyPercentage !== undefined &&
            item.durationSeconds !== null && item.durationSeconds !== undefined &&
            item.numberOfExecutions !== undefined
        ).map(item => ({
            ...item,
            accuracyPercentage: typeof item.accuracyPercentage === 'string'
                ? parseFloat(item.accuracyPercentage)
                : item.accuracyPercentage,
        }));
    }, [rawPerformanceData]);

    const selectedDatasetName = availableDatasets.find(d => d.id === selectedDatasetId)?.name;

    return (
        <div className="page results-layout-page">
            <aside className="results-sidebar">
                <h2 className="sidebar-title">Select Models</h2>
                <p className="sidebar-subtitle">(Max {MAX_SELECTED_MODELS} models)</p>
                {isLoadingModels ? (
                    <p className="loading-text-sidebar">Loading models...</p>
                ) : testedModels.length === 0 ? (
                    <p className="no-data-sidebar">No tested models found.</p>
                ) : (
                    <ul className="model-selection-list">
                        {testedModels.map(model => (
                            <li key={model.id}>
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={selectedModelIds.has(model.id)}
                                        onChange={() => handleModelSelectionChange(model.id)}
                                        disabled={!selectedModelIds.has(model.id) && selectedModelIds.size >= MAX_SELECTED_MODELS && !isLoadingModels}
                                    />
                                    <span>{model.name}</span>
                                </label>
                            </li>
                        ))}
                    </ul>
                )}
            </aside>

            <main className="results-main-content">
                <h1 className="page-title main-content-title">Model Performance Comparison</h1>
                <div className="main-content-filters">
                    <label htmlFor="dataset-select-results">Select Dataset:</label>
                    {isLoadingDatasets && selectedModelIds.size > 0 ? (
                        <span>Loading available datasets...</span>
                    ) : (
                        <select
                            id="dataset-select-results"
                            value={selectedDatasetId}
                            onChange={(e) => setSelectedDatasetId(e.target.value)}
                            disabled={availableDatasets.length === 0 || selectedModelIds.size === 0 || isLoadingDatasets}
                        >
                            {selectedModelIds.size === 0 ? (
                                <option value="" disabled>Select models first</option>
                            ) : availableDatasets.length === 0 && !isLoadingDatasets ? (
                                <option value="" disabled>No common datasets for selected models</option>
                            ) : (
                                <>
                                    <option value="" disabled>-- Select a Dataset --</option>
                                    {availableDatasets.map(dataset => (
                                        <option key={dataset.id} value={dataset.id}>
                                            {dataset.name}
                                        </option>
                                    ))}
                                </>
                            )}
                        </select>
                    )}
                </div>

                {error && <p className="error-text results-error main-content-error">{error}</p>}

                <div className="charts-display-area">
                    <div className="chart-wrapper">
                        {isLoadingChartData ? (
                            <p className="loading-text chart-loading">Loading performance data...</p>
                        ) : processedChartData.length > 0 ? (
                            <CombinedPerformanceBarChart
                                data={processedChartData}
                                datasetName={selectedDatasetName}
                            />
                        ) : selectedModelIds.size > 0 && selectedDatasetId && !isLoadingChartData ? (
                            <p className="no-chart-data">No complete performance data available for this selection.</p>
                        ) : (
                            <p className="no-chart-data">Please select one or more models and a dataset to view performance metrics.</p>
                        )}
                    </div>
                </div>


                {/* --- Data Table Section --- */}
                {processedChartData.length > 0 && !isLoadingChartData && (
                    <div className="results-data-table-container">
                        <h3 className="data-table-title">Detailed Performance Data</h3>
                        <div className="results-data-table">
                            {/* Header Row for Table */}
                            <div className="result-table-row header-row">
                                <span className="result-table-cell header">Model Name</span>
                                <span className="result-table-cell header">Avg. Accuracy (%)</span>
                                <span className="result-table-cell header">Avg. Time (s)</span>
                                <span className="result-table-cell header">Executions</span>
                            </div>
                            {/* Data Rows for Table */}
                            {processedChartData.map((item, index) => (
                                <div key={`${item.modelId}-${item.datasetId}-${index}`} className="result-table-row data-row">
                                    <span className="result-table-cell" title={item.modelName}>{item.modelName}</span>
                                    <span className="result-table-cell">
                                        {/* item.accuracyPercentage is now average and can be null */}
                                        {item.accuracyPercentage !== null ? item.accuracyPercentage.toFixed(2) : 'N/A'}
                                    </span>
                                    <span className="result-table-cell">
                                        {/* item.durationSeconds is now average and can be null */}
                                        {item.durationSeconds !== null ? item.durationSeconds.toFixed(2) : 'N/A'}
                                    </span>
                                    <span className="result-table-cell">{item.numberOfExecutions}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                {/* --- End of Data Table Section --- */}
            </main>
        </div>
    );
};

export default Results;