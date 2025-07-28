import {NavLink} from "react-router-dom";
import {navItems} from "./SideBarData.jsx";
import "./SideBar.css";
import logo from "../../assets/logo.png"
import {useAuth} from "../../Context/AuthContext.tsx";

const Sidebar = () => {
    const { user } = useAuth();

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <img src={logo} alt="Logo" className="sidebar-logo" />
                <span className="sidebar-title">LLMSentinel</span>
            </div>
            <nav className="sidebar-menu">
                {navItems.map((item, index) => (
                    <NavLink
                        to={item.link}
                        className={({ isActive }) =>
                            isActive ? "menu-item active" : "menu-item"
                        } key={index}>
                        {item.icon}
                        <span>{item.text}</span>
                    </NavLink>
                ))}
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
        </div>
    );
};

export default Sidebar;
