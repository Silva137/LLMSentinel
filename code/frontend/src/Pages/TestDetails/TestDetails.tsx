import React, { useEffect, useState } from 'react';
import { useParams} from 'react-router-dom';
import TestService from '../../Services/TestService';
import { Test } from '../../types/Test';
import { QuestionResult } from '../../types/QuestionResult';
import './TestDetails.css';

const TestDetails: React.FC = () => {
    const { testId } = useParams<{ testId: string }>();

    const [test, setTest] = useState<Test | null>(null);
    const [questionResults, setQuestionResults] = useState<QuestionResult[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

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

    const toggleExpand = (index: number) => {
        setExpandedRows((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

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
                            <span className="result-time header">Response Time</span>
                        </div>


                        {/* --- Data Rows --- */}
                        {questionResults.map((result, index) => (
                            <div
                                key={result.id}
                                className={`result-card data-row ${expandedRows.has(index) ? 'expanded' : ''}`}
                                onClick={() => toggleExpand(index)}
                                style={{ cursor: 'pointer' }}
                            >
                                <span className="result-id">{index + 1}</span>
                                <span className="result-question" title={result.question.question}>
                                    {result.question.question }
                                </span>
                                <span className="result-option" title={result.question.option_a}>
                                    {result.question.option_a}
                                </span>
                                <span className="result-option" title={result.question.option_b}>
                                    {result.question.option_b}
                                </span>
                                <span className="result-option" title={result.question.option_c}>
                                    {result.question.option_c}
                                </span>
                                <span className="result-option" title={result.question.option_d}>
                                    {result.question.option_d}
                                </span>
                                <span className={`result-llm-answer ${result.correct ? 'correct' : 'incorrect'}`}>
                                    {result.answer}
                                </span>
                                <span className="result-explanation" title={result.explanation ?? undefined}>
                                    {result.explanation}
                                </span>
                                <span className="result-time">
                                    {result.response_time + 's'}
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