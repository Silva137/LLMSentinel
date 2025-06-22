// src/Services/ResultsService.ts
import api from "./Axios.ts";

export interface SelectableModel {
    id: string; // Ensure this matches backend (string)
    name: string;
}

export interface SelectableDataset {
    id: string; // Ensure this matches backend (string)
    name: string;
}

export interface ModelPerformanceData {
    modelId: string;
    modelName: string;
    datasetId: string;
    datasetName: string;
    accuracyPercentage: number;
    startedAt: string; // ISO string format
    completedAt: string; // ISO string format
    // Calculated on frontend:
    durationSeconds?: number;
}
const ResultsService = {
    getTestedModels: async (): Promise<SelectableModel[]> => {
        try {
            const response = await api.get<SelectableModel[]>('/results/tested-models/');
            return response.data;
        } catch (error) {
            console.error('Error fetching tested models:', error);
            throw error; // Or return [] or null based on your error handling preference
        }
    },

    getAvailableDatasetsForModels: async (modelIds: string[]): Promise<SelectableDataset[]> => {
        if (modelIds.length === 0) {
            // Decide if you want to fetch all user's datasets or none if no models selected
            // For now, let's assume an empty array if no models are passed,
            // or the backend handles empty model_ids to return all user's tested datasets.
            // Adjust queryParams construction if backend expects no model_ids param for all.
        }
        try {
            const queryParams = new URLSearchParams();
            if (modelIds.length > 0) {
                queryParams.append('model_ids', modelIds.join(','));
            }
            // If queryParams is empty, it will just be '/results/available-datasets/'
            const response = await api.get<SelectableDataset[]>(`/results/available-datasets/?${queryParams.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching available datasets:', error);
            throw error;
        }
    },

    getModelsPerformanceDataOnDataset: async (
        modelIds: string[],
        datasetId: string
    ): Promise<ModelPerformanceData[]> => { // Updated return type
        if (!modelIds || modelIds.length === 0 || !datasetId) {
            return [];
        }
        try {
            const queryParams = new URLSearchParams();
            queryParams.append('model_ids', modelIds.join(','));
            queryParams.append('dataset_id', datasetId);

            // Assuming backend endpoint is now /results/models-performance-on-dataset/
            // and returns data matching the ModelPerformanceData interface
            const response = await api.get<ModelPerformanceData[]>(`/results/models-performance-on-dataset/?${queryParams.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching models performance data on dataset:', error);
            throw error;
        }
    },
};

export default ResultsService;