import api from "./Axios.ts";
import {ApiKeyStatus} from "../types/User.ts";

class UserService {

    async getApiKeyStatus(): Promise<ApiKeyStatus> {
        try {
            const response = await api.get("/get-api-key-info/");
            return response.data;
        } catch (error) {
            console.error("Failed to get API key status:", error);
            return { has_key: false };
        }
    }

    async setApiKey(token: string): Promise<ApiKeyStatus | null> {
        try {
            const response = await api.post("/set-api-key/", { api_key: token });
            return response.data
        } catch (error) {
            console.error("Failed to save API key:", error);
            return null;
        }
    }
}

export default new UserService();
