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
}

export default new DatasetService();

