import "./Register.css";
import "../../App.css"
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthService from "../../Services/AuthService.ts";
import * as React from "react";
import { FaEye, FaEyeSlash } from 'react-icons/fa';



const Register = () => {

    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const navigate = useNavigate();

    const handleRegisterSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try{
            await AuthService.register(username, email, password, confirmPassword);
            navigate('/login')
        } catch (error) {
            console.log('Error occurred in register:', error)
        }
    }

    const toggleShowPassword = () => {
        setShowPassword(!showPassword);
    };

    const toggleShowConfirmPassword = () => {
        setShowConfirmPassword(!showConfirmPassword);
    };

    return (
        <div className="login-bg-container">
            <div className="login-form-container">
                <div className="register-text">Register</div>
                <form onSubmit={handleRegisterSubmit}>
                    <input value={username} onChange={e => setUsername(e.target.value)} type="text" className="input" placeholder="Username" required></input>
                    <input value={email} onChange={e => setEmail(e.target.value)} type="email" className="input" placeholder="Email" required></input>
                    <div className="password-input-container">
                        <input
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            type={showPassword ? "text" : "password"}
                            className="input password-field"
                            placeholder="Password"
                            required
                        />
                        <span className="toggle-password-icon" onClick={toggleShowPassword}>
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>
                    <div className="password-input-container">
                        <input
                            value={confirmPassword}
                            onChange={e => setConfirmPassword(e.target.value)}
                            type={showConfirmPassword ? "text" : "password"}
                            className="input password-field"
                            placeholder="Confirm Password"
                            required
                        />
                        <span className="toggle-password-icon" onClick={toggleShowConfirmPassword}>
                            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>
                    <button type="submit" className="register-button">Register</button>
                </form>
                <h2 className="secondary-text">
                    Already have an account? <a href="/login">Login here</a>
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

export default Register;