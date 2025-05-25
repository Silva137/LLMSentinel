export interface QuestionResult {
    id: string | number;
    testId: string | number;
    questionId: string | number;
    llmResponse: string;
    answer: string;
    explanation: string;
    correct: boolean;
    responseTime: number;
}