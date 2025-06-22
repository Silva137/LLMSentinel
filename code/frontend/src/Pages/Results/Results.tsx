// src/Pages/Results/Results.tsx
import React, { useEffect, useState, useMemo } from 'react';
import ResultsService, { SelectableModel, SelectableDataset, ModelPerformanceData } from '../../Services/ResultsService';
import CombinedPerformanceBarChart from '../../Components/PerformaceChart.tsx'; // Ensure correct path
import InfoIcon from '../../assets/infoIcon.svg?react'; // For potential details in table
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
                setError(null); // Clear previous errors when fetching new datasets
                try {
                    const datasets = await ResultsService.getAvailableDatasetsForModels(Array.from(selectedModelIds));
                    setAvailableDatasets(datasets || []);
                    if (datasets && datasets.length > 0) {
                        // If current selectedDatasetId is not in new list, or no dataset is selected, select the first one
                        if (!selectedDatasetId || !datasets.find(d => d.id === selectedDatasetId)) {
                            setSelectedDatasetId(datasets[0].id);
                        }
                    } else {
                        setSelectedDatasetId(''); // No datasets available for selection
                        setRawPerformanceData([]); // Clear chart data if no datasets
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
            setRawPerformanceData([]); // Clear data if no models are selected
        }
    }, [selectedModelIds]); // Removed selectedDatasetId, it will be handled by the next useEffect

    useEffect(() => {
        if (selectedModelIds.size > 0 && selectedDatasetId) {
            const fetchPerformanceData = async () => {
                setIsLoadingChartData(true);
                setError(null); // Clear previous errors
                try {
                    const data = await ResultsService.getModelsPerformanceDataOnDataset(
                        Array.from(selectedModelIds),
                        selectedDatasetId
                    );
                    setRawPerformanceData(data || []);
                } catch (err) {
                    console.error("Failed to fetch performance data:", err);
                    setError("Could not load performance data for the selected dataset.");
                    setRawPerformanceData([]); // Clear data on error
                } finally {
                    setIsLoadingChartData(false);
                }
            };
            fetchPerformanceData();
        } else if (selectedModelIds.size === 0 || !selectedDatasetId) {
            // Clear data if models or dataset are deselected
            setRawPerformanceData([]);
            setIsLoadingChartData(false); // Ensure loading is stopped
        }
    }, [selectedModelIds, selectedDatasetId]); // This effect fetches data based on selections

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
            // When model selection changes, we might need to reset or re-evaluate selectedDatasetId
            // This is handled by the useEffect for availableDatasets
            return newSelected;
        });
    };

    const processedChartData = useMemo((): (ModelPerformanceData & { durationSeconds?: number })[] => {
        return rawPerformanceData.map(item => {
            let durationSeconds: number | undefined = undefined;
            if (item.startedAt && item.completedAt) {
                const start = new Date(item.startedAt).getTime();
                const end = new Date(item.completedAt).getTime();
                if (!isNaN(start) && !isNaN(end) && end >= start) {
                    durationSeconds = (end - start) / 1000;
                }
            }
            return { ...item, durationSeconds };
        }).filter(item => item.accuracyPercentage !== undefined && item.durationSeconds !== undefined && item.modelName !== undefined); // Added modelName check
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
                                    <span>{model.name}</span> {/* Wrapped text in span for styling disabled state */}
                                </label>
                            </li>
                        ))}
                    </ul>
                )}
            </aside>

            <main className="results-main-content">
                <h1 className="page-title main-content-title">Model Performance Comparison</h1>
                <div className="main-content-filters">
                    <label htmlFor="dataset-select-results">Select Dataset:</label> {/* Unique ID */}
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

                {/* --- NEW: Data Table Section --- */}
                {processedChartData.length > 0 && !isLoadingChartData && (
                    <div className="results-data-table-container">
                        <div className="results-data-table">
                            {/* Header Row for Table */}
                            <div className="result-table-row header-row">
                                <span className="result-table-cell header">Model Name</span>
                                <span className="result-table-cell header">Accuracy (%)</span>
                                <span className="result-table-cell header">Time (s)</span>
                                <span className="result-table-cell header">Correct Ans.</span>
                                <span className="result-table-cell header">Total Qs.</span>
                                {/* Add more headers if needed, e.g., for test ID or details button */}
                            </div>
                            {/* Data Rows for Table */}
                            {processedChartData.map((item, index) => (
                                <div key={`${item.modelId}-${item.datasetId}-${index}`} className="result-table-row data-row">
                                    <span className="result-table-cell" title={item.modelName}>{item.modelName}</span>
                                    <span className="result-table-cell">
                                        {item.accuracyPercentage !== undefined ? parseFloat(item.accuracyPercentage.toString()).toFixed(2) : 'N/A'}
                                    </span>
                                    <span className="result-table-cell">
                                        {item.durationSeconds !== undefined ? item.durationSeconds.toFixed(2) : 'N/A'}
                                    </span>
                                    <span className="result-table-cell">{item.correctAnswers ?? 'N/A'}</span>
                                    <span className="result-table-cell">{item.totalQuestions ?? 'N/A'}</span>
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