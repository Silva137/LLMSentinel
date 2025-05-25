import {Dataset} from "./Dataset.ts";

export interface Question {
    id: number;
    dataset: Dataset;
    question: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    explanation: string | null;
}
