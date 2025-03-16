import api from "./Axios.ts";
import {User} from "../types/User.ts";

class AuthService {

    async login(username: string, password: string): Promise<boolean> {
        try {
            const response = await api.post("/auth/login/", { username, password });
            return response.data.success;
        } catch (error) {
            console.error("Login failed:", error);
            return false;
        }
    }

    async register(username: string, email: string, password: string, password2: string): Promise<boolean> {
        try {
            const response = await api.post("/auth/register/", { username, email, password, password2 });
            return response.data.success;
        } catch (error) {
            console.error("Register failed:", error);
            return false;
        }
    }

    async logout(): Promise<boolean> {
        try {
            const response = await api.post("/auth/logout/");
            return response.data.success;
        } catch (error) {
            console.error("Logout failed:", error);
            return false;
        }
    }

    async refreshToken(): Promise<boolean> {
        try {
            const response = await api.post("/auth/refresh/");
            return response.data.success;
        } catch (error) {
            console.error("Token refresh failed:", error);
            return false;
        }
    }

    async authenticated_user(): Promise<User | null> {
        try {
            const response = await api.get("/auth/authenticated/");
            return response.data.user;
        } catch (error) {
            console.log('here')
            console.error("Fetching authenticated user failed:", error);
            return null;
        }
    }
}

export default new AuthService();
