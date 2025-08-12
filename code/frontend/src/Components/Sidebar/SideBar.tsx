import {NavLink} from "react-router-dom";
import {navItems} from "./SideBarData.jsx";
import "./SideBar.css";
import logo from "../../assets/logo.png"
import {useAuth} from "../../Context/AuthContext.tsx";
import {useState} from "react";
import ApiKeyModal from "../ApiKeyModal/ApiKeyModal.tsx";

const Sidebar = () => {
    const { user } = useAuth();
    const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <img src={logo} alt="Logo" className="sidebar-logo" />
                <span className="sidebar-title">LLMSentinel</span>
            </div>
            <nav className="sidebar-menu">
                {navItems.map((item, index) => {
                    if (item.text === "Settings") {
                        return (
                            <div
                                key={index}
                                className="menu-item"
                                onClick={() => setIsApiKeyModalOpen(true)}
                            >
                                {item.icon}
                                <span>{item.text}</span>
                            </div>
                        );
                    }

                    if (item.link) {
                        return (
                            <NavLink
                                to={item.link}
                                key={index}
                                className={({ isActive }) =>
                                    "menu-item" + (isActive ? " active" : "")
                                }
                            >
                                {item.icon}
                                <span>{item.text}</span>
                            </NavLink>
                        );
                    }
                    return null; // Ou um item não clicável se preferir
                })}
            </nav>

            {user && (
                <div className="sidebar-user-card">
                    <div className="sidebar-user-avatar">
                        {user.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="sidebar-user-info">
                        <span className="sidebar-user-name">{user.username}</span>
                        <span className="sidebar-user-email">{user.email}</span>
                    </div>
                </div>
            )}

            <ApiKeyModal
                isOpen={isApiKeyModalOpen}
                onClose={() => setIsApiKeyModalOpen(false)}
            />

        </div>


    );
};

export default Sidebar;
