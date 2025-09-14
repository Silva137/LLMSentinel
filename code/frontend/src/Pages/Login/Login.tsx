import "./Login.css";
import "../../App.css"
import {useState} from "react";
import { useAuth } from "../../Context/AuthContext.tsx";
import * as React from "react";
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { Alert } from "@mui/material";
import {useLocation, useNavigate} from "react-router-dom";


const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const location = useLocation();
    const navigate = useNavigate();
    const successRegister = (location.state as { message?: string } | null)?.message;

    const {login} = useAuth();

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        const success = await login(username, password);
        if (!success) {
            setError("Invalid Credentials");
        }
    };

    const toggleShowPassword = () => {
        setShowPassword(!showPassword);
    };

    return (
        <div className="login-bg-container">

            {successRegister && (
                <Alert
                    className="custom-success-alert"
                    variant="filled"
                    severity="success"
                    onClose={() => navigate(location.pathname, { replace: true })}
                >
                    {successRegister}
                </Alert>
            )}

            <div className="login-form-container">
                <div className="login-text">Log in</div>

                <form onSubmit={handleLoginSubmit}>
                    <input
                        onChange={e => setUsername(e.target.value)}
                        type="text"
                        className="input"
                        placeholder="Username"
                        required
                    />
                    <div className="password-input-container">
                        <input
                            onChange={(e) => setPassword(e.target.value)}
                            type={showPassword ? "text" : "password"}
                            className="input password-field"
                            placeholder="Password"
                            required
                        />
                        <span className="toggle-password-icon" onClick={toggleShowPassword}>
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>

                    {error && (
                            <Alert
                                className="custom-error-alert"
                                variant="filled"
                                severity="error"
                                onClose={() => setError(null)}
                            >
                                {error}
                            </Alert>
                    )}

                    <button type="submit" className="login-button">Log in</button>
                </form>
                <h2 className="secondary-text" >
                    Do not have an account? <a href="/register">Register here</a>
                </h2>
            </div>
            <div className="hero-text-container">
                <h1 className="hero-text">
                    <span>Create,</span><br />
                    <span>Test,</span><br />
                    <span>Defend.</span>
                </h1>
            </div>
        </div>
    );
};

export default Login;