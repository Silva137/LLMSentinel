import { useEffect, useState } from "react";
import "./Models.css";

interface Model {
    id: number;
    name: string;
    provider: string;
    description: string;
}

const Models = () => {
    const [models, setModels] = useState<Model[]>([]);

    useEffect(() => {
        // Simula uma chamada à API (substitui por chamada real à API quando estiver pronta)
        const fetchModels = async () => {
            const mockData: Model[] = [
                { id: 1, name: "GPT-4", provider: "OpenAI", description: "Advanced LLM by OpenAI" },
                { id: 2, name: "Claude 3", provider: "Anthropic", description: "Constitutional AI model" },
                { id: 3, name: "Gemini Flash 1.5", provider: "Google", description: "High-speed model for generation tasks" },
                { id: 4, name: "LLaMA 3", provider: "Meta", description: "Efficient open-source LLM" },
            ];
            setModels(mockData);
            console.log(mockData)
        };

        fetchModels();
    }, []);

    return (
        <div className="models-page">
            <h2 className="models-title">Available LLMs</h2>
            <div className="models-grid">
                {models.map((model) => (
                    <div key={model.id} className="model-card">
                        <h3>{model.name}</h3>
                        <p className="provider">{model.provider}</p>
                        <p className="description">{model.description}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Models;
