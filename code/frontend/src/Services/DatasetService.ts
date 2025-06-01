import api from "./Axios.ts";
import {Dataset} from "../types/Dataset.ts";
import {Question} from "../types/Question.ts";

class DatasetService {

    async getAllDatasets(): Promise<Dataset[] | null> {
        try {
            const response = await api.get("/datasets/");
            return response.data;
        } catch (error) {
            console.error("Fetching datasets failed:", error);
            return null;
        }
    }

    async getQuestionsByDatasetId(datasetId: string | undefined): Promise<Question[] | null> {
        try {
            if (!datasetId) return null;
            const response = await api.get(`/questions/dataset/${datasetId}/`);
            return response.data;
        } catch (error) {
            console.error("Fetching questions failed:", error);
            return null;
        }
    }

    async getPublicDatasets(): Promise<Dataset[] | null> {
        try {
            const response = await api.get("/datasets/", {
                params: {
                    is_public: true
                }
            });
            return response.data;
        } catch (error) {
            console.error("Fetching public datasets failed:", error);
            return null;
        }
    }

    async uploadDataset(name: string, description: string, file: File): Promise<{ message: string } | null> {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('file', file);

        try {
            const response = await api.post('/datasets/upload/', formData);
            return response.data;
        } catch (error) {
            console.error("Upload dataset failed:", error);
            return null;
        }
    }
}

export default new DatasetService();

