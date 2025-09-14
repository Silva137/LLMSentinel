import {User} from "./User.ts";

export interface Dataset {
    id: number;
    name: string;
    total_questions: number;
    description: string | null;
    is_public: boolean;
    owner: User;
    origin: Dataset;
}