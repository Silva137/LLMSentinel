import React, { useEffect, useState } from "react";
import TestService from "../../Services/TestService";
import "./Evaluations.css";
import { Test } from "../../types/Test";
import { useNavigate } from "react-router-dom";
import SearchIcon from "../../assets/searchIcon.svg?react";

const truncateText = (text: string | null | undefined, maxLength: number): string => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

const Evaluations: React.FC = () => {
    const [tests, setTests] = useState<Test[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const navigate = useNavigate();

    const fetchTests = async () => {
        setIsLoading(true);
        const data = await TestService.getAllTests();
        setTests(data || [])
        setIsLoading(false);
    };

    const handleTestDetailsClick = (testId: string | number) => {
        navigate(`/evaluations/${testId}/results`);
    };

    const handleDeleteClick = (testId: string | number) => {
        console.log(`Delete test with ID: ${testId}`);
        //todo
    };

    const handleCreateTest = async () => {
        //todo
    };

    useEffect(() => {
        fetchTests();
    }, []);

    return (
        <div className="page">
            <h1 className="page-title">Evaluations</h1>

            <div className="tests-list-container">
                {isLoading ? (
                    <p className="loading-text">Loading Tests...</p>
                ) : tests.length === 0 ? (
                    <p className="no-tests-text">No Tests available.</p>
                ) : (
                    <div className="tests-list">
                        {/* --- Header Row --- */}
                        <div className="test-card header-row">
                            <span className="test-id header">ID</span>
                            <span className="test-dataset header">Dataset</span>
                            <span className="test-llm-model header">LLM Model</span>
                            <span className="test-correct-answers header">Correct Answers</span>
                            <span className="test-accuracy header">Accuracy</span>
                        </div>

                        {/* --- Data Rows --- */}
                        {tests.map((test, index) => (
                            <div
                                key={test.id}
                                className="test-card data-row"
                            >
                                <span className="test-id">{index + 1}</span>
                                <span className="test-dataset" title={test.dataset.name}>
                                    {truncateText(test.dataset.name, 30)}
                                </span>
                                <span className="test-model" title={test.llm_model.name || 'N/A'}>
                                    {truncateText(test.llm_model.name, 20)}
                                </span>
                                <span className="test-correct-answers" title={test.correct_answers.toString() || 'N/A'}>
                                    {truncateText(test.correct_answers.toString(), 20)}
                                </span>
                                <span className="test-accuracy" title={test.accuracy_percentage.toString() || 'N/A'}>
                                    {truncateText(test.accuracy_percentage.toString(), 20)}
                                </span>
                                <div className="details-button-container">
                                    <button
                                        className="details-button"
                                        onClick={() => handleTestDetailsClick(test.id)}
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

export default Evaluations;