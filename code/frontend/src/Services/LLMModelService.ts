import api from "./Axios.ts";
import { LLMModel } from "../types/LLMModel.ts";

class LLMModelService {

    async getAllLLMModels(): Promise<LLMModel[] | null> {
        try {
            const response = await api.get("/llm-models/");
            return response.data;
        } catch (error) {
            console.error("Fetching LLM models failed:", error);
            return null;
        }
    }

    async searchLLMModelsByName(name: string): Promise<LLMModel[] | null> {
        try {
            if (name.trim().length === 0) {
                return this.getAllLLMModels();
            }
            const response = await api.get(`/llm-models/?name=${encodeURIComponent(name)}`);
            return response.data;
        } catch (error) {
            console.error(`Searching LLM models by name "${name}" failed:`, error);
            return null;
        }
    }
}

export default new LLMModelService();