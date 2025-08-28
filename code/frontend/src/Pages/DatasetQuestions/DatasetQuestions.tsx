import React, { useEffect, useState } from "react";
import DatasetService from "../../Services/DatasetService.ts";
import "./DatasetQuestions.css";
import {Question} from "../../types/Question.ts";
import {Link, useParams} from "react-router-dom";
import {Dataset} from "../../types/Dataset.ts";

const DatasetQuestions: React.FC = () => {
    const { datasetId } = useParams<{ datasetId: string }>();
    const [dataset, setDataset] = useState<Dataset>();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());


    const fetchDatasetInfo = async () => {
        setIsLoading(true);
        const data = await DatasetService.getDatasetById(datasetId);
        const questions = await DatasetService.getQuestionsByDatasetId(datasetId);
        console.log(questions);
        setDataset(data || undefined);
        setQuestions(questions || []);
        setIsLoading(false);
    };


    useEffect(() => {
        fetchDatasetInfo();
    }, []);

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
            <h1 className="page-title breadcrumb-title">
                <Link to="/datasets">Datasets</Link>
                <span>&gt;</span>
                <span>{dataset?.name}</span>
            </h1>

            <div className="questions-list-container">
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
                            <span className="q-correct header">Correct Answer</span>
                        </div>

                        {/* --- Data Rows --- */}
                        {questions.map((question, index) => (
                            <div
                                key={question.id}
                                className={`question-list-card data-row ${expandedRows.has(index) ? 'expanded' : ''}`}
                                onClick={() => toggleExpand(index)}
                                style={{ cursor: 'pointer' }}
                            >
                                <span className="q-id">{question.id}</span>
                                <span className="q-text" title={question.question}>
                                    {question.question}
                                </span>
                                <span className="q-option" title={question.option_a}>
                                     {question.option_a}
                                </span>
                                <span className="q-option" title={question.option_b}>
                                     {question.option_b}
                                </span>
                                <span className="q-option" title={question.option_c}>
                                     {question.option_c}
                                </span>
                                <span className="q-option" title={question.option_d}>
                                     {question.option_d}
                                </span>
                                <span className="q-correct">
                                    {question.correct_option}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DatasetQuestions;