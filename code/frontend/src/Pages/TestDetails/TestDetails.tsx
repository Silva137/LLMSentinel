import React, { useEffect, useState } from 'react';
import { useParams} from 'react-router-dom';
import TestService from '../../Services/TestService';
import { Test } from '../../types/Test';
import { QuestionResult } from '../../types/QuestionResult';
import InfoIcon from '../../assets/infoIcon.svg?react';
import './TestDetails.css';

// Helper function for text truncation
const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

const TestDetails: React.FC = () => {
    const { testId } = useParams<{ testId: string }>();

    const [test, setTest] = useState<Test | null>(null);
    const [questionResults, setQuestionResults] = useState<QuestionResult[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const fetchTestDetails = async () => {
        setIsLoading(true);
        if (!testId) {
            console.error("Test ID is not provided");
            setIsLoading(false);
            return;
        }
        const data = await TestService.getTestById(testId);
        console.log(data);
        setTest(data || null);
        setQuestionResults(data?.results || []);
        setIsLoading(false);

    };

    useEffect(() => {
        fetchTestDetails();
    }, [testId]);


    return (
        <div className="page">
            <h1 className="page-title">Question Results</h1>

            <div className="results-list-container">
                {isLoading ? (
                    <p className="loading-text">Loading results...</p>
                ) : questionResults.length === 0 ? (
                    <p className="no-results-text">No results found for this test.</p>
                ) : (
                    <div className="results-list">
                        {/* --- Header Row --- */}
                        <div className="result-card header-row">
                            <span className="result-id header">ID</span>
                            <span className="result-question header">Question</span>
                            <span className="result-option header">Option A</span>
                            <span className="result-option header">Option B</span>
                            <span className="result-option header">Option C</span>
                            <span className="result-option header">Option D</span>
                            <span className="result-llm-answer header">LLM Answer</span>
                            <span className="result-explanation header">Explanation</span>
                            <span className="result-actions header"></span>
                        </div>


                        {/* --- Data Rows --- */}
                        {questionResults.map((result, index) => (
                            <div key={result.id} className="result-card data-row">
                                <span className="result-id">{index + 1}</span>
                                <span className="result-question" title={result.question.question}>
                                    {truncateText(result.question?.question, 15)}
                                </span>
                                <span className="result-option" title={result.question?.option_a}>
                                     {truncateText(result.question?.option_a, 15)}
                                 </span>
                                <span className="result-option" title={result.question?.option_b}>
                                     {truncateText(result.question?.option_b, 15)}
                                 </span>
                                <span className="result-option" title={result.question?.option_c}>
                                     {truncateText(result.question?.option_c, 15)}
                                 </span>
                                <span className="result-option" title={result.question?.option_d}>
                                     {truncateText(result.question?.option_d, 15)}
                                 </span>
                                <span className={`result-llm-answer ${result.correct ? 'correct' : 'incorrect'}`}>
                                    {result.answer}
                                </span>
                                <span className="result-explanation" title={result.explanation ?? undefined}>
                                    {truncateText(result.explanation, 20)}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TestDetails;
