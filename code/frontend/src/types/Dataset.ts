import {User} from "./User.ts";

export interface Dataset {
    id: number;
    name: string;
    description: string | null;
    is_public: boolean;
    owner: User
}