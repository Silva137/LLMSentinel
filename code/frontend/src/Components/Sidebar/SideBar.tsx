import { Link } from "react-router-dom";
import {navItems} from "./SideBarData.jsx";
import "./Sidebar.css";

const Sidebar = () => {
    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <img src="../../" alt="Logo" className="sidebar-logo" />
                <span className="sidebar-title">LLMSentinel</span>
            </div>
            <nav className="sidebar-menu">
                {navItems.map((item, index) => (
                    <Link to={item.link} className="menu-item" key={index}>
                        {item.icon}
                        <span>{item.text}</span>
                    </Link>
                ))}
            </nav>
        </div>
    );
};

export default Sidebar;
