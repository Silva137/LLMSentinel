import { useAuth } from "../Context/AuthContext.tsx";
import {useState} from "react";
import DatasetService from "../Services/DatasetService.ts";
import {Dataset} from "../types/Dataset.ts";

const Dashboard = () => {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [loading, setLoading] = useState(false);
    const { user, logout } = useAuth();

    const fetchDatasets = async () => {
        setLoading(true);
        const data = await DatasetService.getAllDatasets();
        if (data){
            setDatasets(data);
            console.log(data)
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Dashboard</h2>
            {user ? (
                <>
                    <p>Welcome, {user.username}</p>
                    <button onClick={logout}>Logout</button>
                    <br />
                    <button onClick={fetchDatasets}>Get Datasets</button>

                    {loading && <p>Loading datasets...</p>}

                    {datasets.length > 0 ? (
                        <ul>
                            {datasets.map((dataset: Dataset) => (
                                <li key={dataset.id}>{dataset.name}</li>
                            ))}
                        </ul>
                    ) : (
                        !loading && <p>No datasets available.</p>
                    )}
                </>
            ) : (
                <p>You are not logged in.</p>
            )}
        </div>
    );
};

export default Dashboard;
