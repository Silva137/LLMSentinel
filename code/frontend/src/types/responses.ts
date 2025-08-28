export interface RegisterResponse {
    success: boolean;
    message: string;
    user: {
        id: number;
        username: string;
        email: string;
    };
}