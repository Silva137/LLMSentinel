// src/Components/Charts/CombinedPerformanceBarChart.tsx
import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Label
} from 'recharts';
import { ModelPerformanceData } from '../Services/ResultsService.ts'; // Adjust path

interface Props {
    data: ModelPerformanceData[];
    datasetName?: string;
}

const PerformanceChart: React.FC<Props> = ({ data, datasetName }) => {
    if (!data || data.length === 0) {
        return <p className="no-chart-data-message">No performance data to display.</p>;
    }

    const chartContent = (
        <BarChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 70 }}
        >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
                dataKey="modelName"
                angle={-25}
                textAnchor="end"
                height={30}
                interval={0}
                tick={{ fontSize: 11 }}
            />
            <YAxis
                yAxisId="accuracy"
                orientation="left"
                stroke="#8884d8"
                domain={[0, 100]}
                tickFormatter={(tick) => `${tick}%`}
            >
                <Label value="Accuracy (%)" angle={-90} position="insideLeft" style={{ textAnchor: 'middle', fill: '#8884d8' }} />
            </YAxis>
            <YAxis
                yAxisId="time"
                orientation="right"
                stroke="#82ca9d"
                tickFormatter={(tick) => `${tick.toFixed(1)}s`}
            >
                <Label value="Execution Time (s)" angle={-90} position="insideRight" style={{ textAnchor: 'middle', fill: '#82ca9d' }} />
            </YAxis>
            <Tooltip
                contentStyle={{ backgroundColor: '#2f354c', border: '1px solid #4a5175', borderRadius: '5px' }}
                itemStyle={{ color: '#e0e4ff' }}
                formatter={(value: number, name: string) => {
                    if (name === 'Accuracy') return [`${(value as number).toFixed(1)}%`, name];
                    if (name === 'Execution Time') return [`${(value as number).toFixed(2)}s`, name];
                    return [value, name];
                }}
            />
            <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: '20px' }} />
            <Bar yAxisId="accuracy" dataKey="accuracyPercentage" fill="#8884d8" name="Accuracy" barSize={50} animationDuration={2000} />
            <Bar yAxisId="time" dataKey="durationSeconds" fill="#82ca9d" name="Execution Time" barSize={50} animationDuration={2000} />
        </BarChart>
    );

    return (
        <>
            <h3 className="chart-title-header">{`Model Performance on "${datasetName}"`}</h3>
            <ResponsiveContainer width="100%" height={550}>
                {chartContent}
            </ResponsiveContainer>
        </>
    );
};

export default PerformanceChart;