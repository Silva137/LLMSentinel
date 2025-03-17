import {createContext, useContext, useState, useEffect, ReactNode} from 'react';
import { useNavigate } from 'react-router-dom';
import {User} from "../types/User.ts";
import AuthService from "../Services/AuthService.ts";

interface AuthContextType {
    user: User | null;
    login: (username: string, password: string) => Promise<boolean>;
    logout: () => Promise<void>;
    loading: boolean;
}


const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {

    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const get_authenticated_user = async () => {
        try {
            const user = await AuthService.authenticated_user();
            setUser(user);
            console.log("get_authenticated_user", user);
        } catch (error) {
            console.error("Error fetching authenticated user:", error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (username: string, password: string) => {
        const success = await AuthService.login(username, password);
        if (success) {
            const user = await AuthService.authenticated_user();
            setUser(user);
            setLoading(false);
            navigate('/dashboard');
        } else
            alert('Incorrect username or password')

        return success;
    }


    const logout = async () => {
        await AuthService.logout();
        setUser(null);
        navigate("/login");
    };



    useEffect(() => {
        const unprotectedRoutes = ["/login", "/register", "/"];
        const currentPath = window.location.pathname;

        if (!unprotectedRoutes.includes(currentPath)) {
            get_authenticated_user();
        }
    }, []);


    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context)
        throw new Error("useAuth must be used within an AuthProvider");

    return context;
}
