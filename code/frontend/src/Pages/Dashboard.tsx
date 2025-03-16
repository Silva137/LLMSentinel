import { useAuth } from "../Context/AuthContext.tsx";

const Dashboard = () => {
    const { user, logout } = useAuth();

    return (
        <div>
            <h2>Dashboard</h2>
            {user ? (
                <>
                    <p>Welcome, {user.username}!</p>
                    <button onClick={logout}>Logout</button>
                </>
            ) : (
                <p>You are not logged in.</p>
            )}
        </div>
    );
};

export default Dashboard;
