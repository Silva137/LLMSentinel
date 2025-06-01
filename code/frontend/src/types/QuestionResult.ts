import {Question} from "./Question.ts";

export interface QuestionResult {
    id: string | number;
    testId: string | number;
    question: Question;
    llmResponse: string;
    answer: string;
    explanation: string;
    correct: boolean;
    responseTime: number;
}