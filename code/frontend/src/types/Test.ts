import {Dataset} from "./Dataset.ts";
import {LLMModel} from "./LLMModel.ts";
import {QuestionResult} from "./QuestionResult.ts";

export interface Test {
    id: string | number;
    dataset: Dataset;
    llm_model: LLMModel;
    correct_answers: number;
    accuracy_percentage: number;
    results: QuestionResult[];
}