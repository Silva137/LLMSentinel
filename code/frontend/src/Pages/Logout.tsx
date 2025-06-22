import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../Context/AuthContext.tsx";

const Logout: React.FC = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();


    const performLogout = async () => {
        await logout();
        navigate("/login");
    };

    useEffect(() => {
        performLogout();
    }, [logout, navigate]);

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <p>Logging out...</p>
            {/* You could add a spinner component here */}
        </div>
    );
};

export default Logout;