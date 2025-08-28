import "./Register.css";
import "../../App.css"
import { useState} from 'react';
import { useNavigate } from 'react-router-dom';
import AuthService from "../../Services/AuthService.ts";
import * as React from "react";
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import {RegistrationErrors} from "../../types/errors.ts";
import axios from "axios";
import { Alert } from '@mui/material';

const Register = () => {

    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const [errors, setErrors] = useState<RegistrationErrors>({});
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleRegisterSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});
        setIsLoading(true);

        if (password !== confirmPassword) {
            setErrors({ non_field_errors: ["Passwords do not match"] });
            setIsLoading(false);
            return;
        }

        try{
            const response = await AuthService.register(username, email, password, confirmPassword);
            console.log("Registration successful:", response.message);
            navigate('/login', { state: { message: "Registration successful!" } })
        } catch (error) {
            console.log('Error occurred during registration:', error)

            if (axios.isAxiosError(error) && error.response) {
                const registrationErrors: RegistrationErrors = error.response.data.error;
                setErrors(registrationErrors);
            } else {
                    setErrors({ non_field_errors: ["An unexpected error occurred. Please try again later."] });
                }
        } finally {
            setIsLoading(false);
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

                    <input value={username} onChange={e => setUsername(e.target.value)} type="text" className={`input ${errors.username ? "input-error" : ""}`} placeholder="Username" required></input>
                    <div className="alert-container">
                        {errors.username?.[0] && <Alert severity="error" variant="filled">{errors.username[0]}</Alert>}
                    </div>


                    <input value={email} onChange={e => setEmail(e.target.value)} type="email" className={`input ${errors.email ? "input-error" : ""}`} placeholder="Email" required></input>
                    <div className="alert-container">
                        {errors.email?.[0] && <Alert severity="error" variant="filled">{errors.email[0]}</Alert>}
                    </div>


                    <div className="password-input-container">
                        <input
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            type={showPassword ? "text" : "password"}
                            className={`input password-field${errors.password ? "input-error" : ""}`}
                            placeholder="Password"
                            required
                        />
                        <span className="toggle-password-icon" onClick={toggleShowPassword}>
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>
                    <div className="alert-container">
                        {errors.password?.[0] && <Alert severity="error" variant="filled">{errors.password[0]}</Alert>}
                    </div>


                    <div className="password-input-container">
                        <input
                            value={confirmPassword}
                            onChange={e => setConfirmPassword(e.target.value)}
                            type={showConfirmPassword ? "text" : "password"}
                            className={`input password-field${errors.password ? "input-error" : ""}`}
                            placeholder="Confirm Password"
                            required
                        />
                        <span className="toggle-password-icon" onClick={toggleShowConfirmPassword}>
                            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>
                    <div className="alert-container">
                        {errors.password2?.[0] && <Alert severity="error" variant="filled">{errors.password2[0]}</Alert>}
                    </div>

                    {errors.non_field_errors?.[0] && (
                        <div className="alert-container">
                            <Alert severity="error" variant="filled">{errors.non_field_errors[0]}</Alert>
                        </div>
                    )}

                    <button type="submit" className="register-button" disabled={isLoading}>
                        {isLoading ? 'Registering...' : 'Register'}
                    </button>
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