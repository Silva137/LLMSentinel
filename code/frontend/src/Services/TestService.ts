import api from "./Axios.ts";
import { Test } from '../types/Test';


class TestService {

    async getAllTests(datasetName?: string, llmModelName?: string): Promise<Test[] | null> {
        try {
            const queryParams = new URLSearchParams();
            if (datasetName) queryParams.append('dataset_name', datasetName);
            if (llmModelName) queryParams.append('llm_model_name', llmModelName);

            const response = await api.get("/tests/?" + queryParams.toString());
            return response.data;
        } catch (error) {
            console.error("Fetching Tests failed:", error);
            return null;
        }
    }

    async getTestById(testId: string): Promise<Test | null> {
        try {
            const response = await api.get(`/tests/${testId}/`);
            return response.data;
        } catch (error) {
            console.error(`Fetching test ${testId} failed:`, error);
            return null;
        }
    }

    async createTest(datasetName: string, llmModelName: string): Promise<Test | null> {
        try {
            const response = await api.post("/tests/", {
                dataset_name: datasetName,
                llm_model_name: llmModelName,
            });
            return response.data;
        } catch (error) {
            console.error("Creating test failed:", error);
            return null;
        }
    }
}

export default new TestService();