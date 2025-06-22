import "./Login.css";
import "../../App.css"
import { useState } from "react";
import { useAuth } from "../../Context/AuthContext.tsx";
import * as React from "react";
import { FaEye, FaEyeSlash } from 'react-icons/fa';

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const {login} = useAuth();

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(username, password);
        if (!success) {
            alert("Invalid credentials");
        }
    };

    const toggleShowPassword = () => {
        setShowPassword(!showPassword);
    };

    return (
        <div className="login-bg-container">
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