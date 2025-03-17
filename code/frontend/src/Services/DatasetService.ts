import api from "./Axios.ts";
import {Dataset} from "../types/Dataset.ts";

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

    async getDatasetById(id: number): Promise<Dataset | null> {
        try {
            const response = await api.get(`/datasets/${id}/`);
            return response.data;
        } catch (error) {
            console.error(`Fetching dataset with ID ${id} failed:`, error);
            return null;
        }
    }
}

export default new DatasetService();