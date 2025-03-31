import {NavLink, useNavigate } from "react-router-dom";
import {navItems} from "./SideBarData.jsx";
import "./Sidebar.css";
import logo from "../../assets/logo.png"

const Sidebar = () => {
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
        </div>
    );
};

export default Sidebar;
