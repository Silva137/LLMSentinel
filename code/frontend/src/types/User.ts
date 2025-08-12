export interface User {
    id: number;
    username: string;
    email: string;
}

export interface ApiKeyStatus {
    has_key: boolean;
    last4?: string;
}

