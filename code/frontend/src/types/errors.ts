export interface RegistrationErrors {
    username?: string[];
    email?: string[];
    password?: string[];
    password2?: string[];
    non_field_errors?: string[];
}

export interface CreateTestErrors {
    code?: string;
    error?: string;
}