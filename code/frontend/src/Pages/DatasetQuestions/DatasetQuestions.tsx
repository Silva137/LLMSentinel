import React, { useEffect, useState } from "react";
import DatasetService from "../../Services/DatasetService.ts";
import "./DatasetQuestions.css";
import SearchIcon from "../../assets/searchIcon.svg?react";
import {Question} from "../../types/Question.ts";
import {useParams} from "react-router-dom";


const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

const DatasetQuestions: React.FC = () => {
    const { datasetId } = useParams<{ datasetId: string }>();

    const [questions, setQuestions] = useState<Question[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const fetchDatasetQuestions = async () => {
        setIsLoading(true);
        const data = await DatasetService.getQuestionsByDatasetId(datasetId);
        console.log(data);
        setQuestions(data || []);
        setIsLoading(false);
    };


    useEffect(() => {
        fetchDatasetQuestions();
    }, []);

    return (
        <div className="page">
            <h1 className="page-title">Datasets</h1>

            <div className="questions-list-container"> {/* Re-use container style concept */}
                {isLoading ? (
                    <p className="loading-text">Loading questions...</p>
                ) : questions.length === 0 ? (
                    <p className="no-questions-text">No questions found for this dataset.</p>
                ) : (
                    <div className="questions-list">
                        {/* --- Header Row --- */}
                        <div className="question-list-card header-row">
                            <span className="q-id header">ID</span>
                            <span className="q-text header">Question</span>
                            <span className="q-option header">Option A</span>
                            <span className="q-option header">Option B</span>
                            <span className="q-option header">Option C</span>
                            <span className="q-option header">Option D</span>
                            <span className="q-correct header">Correct</span>
                            <span className="q-explanation header">Explanation</span>
                            <span className="q-details-button-container header"></span>
                        </div>

                        {/* --- Data Rows --- */}
                        {questions.map((question) => (
                            <div key={question.id} className="question-list-card data-row">
                                <span className="q-id">{question.id}</span>
                                <span className="q-text" title={question.question}>
                                    {truncateText(question.question, 25)} {/* Adjust truncation */}
                                </span>
                                <span className="q-option" title={question.option_a}>
                                     {truncateText(question.option_a, 15)}
                                </span>
                                <span className="q-option" title={question.option_b}>
                                     {truncateText(question.option_b, 15)}
                                </span>
                                <span className="q-option" title={question.option_c}>
                                     {truncateText(question.option_c, 15)}
                                </span>
                                <span className="q-option" title={question.option_d}>
                                     {truncateText(question.option_d, 15)}
                                </span>
                                <span className="q-correct">
                                    {question.correct_option}
                                </span>
                                <span className="q-explanation" title={question.explanation || "N/A"}>
                                    {truncateText(question.explanation, 20)}
                                </span>
                                <div className="q-details-button-container">
                                    <button
                                        className="details-button"
                                        onClick={() => "TODO: Handle question details click"}
                                        title="View Full Question Details"
                                    >
                                        <SearchIcon className="details-icon" />
                                        Details
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DatasetQuestions;