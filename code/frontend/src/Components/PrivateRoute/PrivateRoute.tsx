import {Navigate, Outlet} from "react-router-dom";
import { useAuth } from "../../Context/AuthContext.tsx";
import Sidebar from "../Sidebar/SideBar.tsx";
import "./PrivateRoute.css";

const PrivateRoute = () => {
    const { user, loading } = useAuth();

    if (loading) return <p>Loading...</p>;

    return user ? (
        <div className="main-layout">
            <Sidebar />
            <div className="main-content">
                <Outlet />
            </div>
        </div>
    ) : (
        <Navigate to="/login" />
    );
};

export default PrivateRoute;