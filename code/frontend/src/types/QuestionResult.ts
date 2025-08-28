import {Question} from "./Question.ts";

export interface QuestionResult {
    id: string | number;
    testId: string | number;
    question: Question;
    llmResponse: string;
    answer: string;
    correct: boolean;
    response_time: number;
}