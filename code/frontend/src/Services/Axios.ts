import axios, {AxiosInstance} from "axios";
import AuthService from "./AuthService.ts";

const api: AxiosInstance = axios.create({
    baseURL: "http://localhost:8001/api",
    withCredentials: true,                  // allow cookies
});


let refreshPromise: Promise<boolean> | null = null;

// Refresh-token logic
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        // Check if the error is due to an unauthorized response and the request hasn't been retried
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            // If there's no refresh promise already in progress, start one
            if (!refreshPromise) {
                refreshPromise = (async () => {
                    try{
                        const success = await AuthService.refreshToken();
                        refreshPromise = null;
                        if (!success) {
                            console.error("Refresh token failed");
                            await AuthService.logout();
                            window.location.href = "/login";
                        }
                        return success;
                    } catch (err) {
                        console.error("Refresh token request failed:", err);
                        refreshPromise = null;
                        return false;
                    }
                })();
            }

            try {
                const success = await refreshPromise;
                console.log('Refresh-Token',success);
                refreshPromise = null;
                return api(originalRequest);
            } catch (err) {
                refreshPromise = null;
                return Promise.reject(err);
            }
        }
        return Promise.reject(error);
    }
);


export default api;
