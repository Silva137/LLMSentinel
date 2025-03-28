import "./Login.css";
import "../../App.css"
import { useState } from "react";
import { useAuth } from "../../Context/AuthContext.tsx";
import * as React from "react";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const {login} = useAuth();

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(username, password);
        if (!success) {
            alert("Invalid credentials");
        }
    };

    return (
        <div className="login-bg-container">
            <div className="login-form-container">
                <div className="login-text">Log in</div>
                <form onSubmit={handleLoginSubmit}>
                    <input onChange={e => setUsername(e.target.value)} type="username" className="input" placeholder="Username" required></input>
                    <input onChange={e => setPassword(e.target.value)} type="password" className="input" placeholder="Password" required></input>
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