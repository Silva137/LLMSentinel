import { JSX } from "react";

import ModelsIcon from "../../assets/modelsIcon.svg?react";
import DatasetsIcon from "../../assets/datasetsIcon.svg?react";
import EvaluationsIcon from "../../assets/evaluationsIcon.svg?react";
import ResultsIcon from "../../assets/resultsIcon.svg?react";
import CommunityIcon from "../../assets/communityIcon.svg?react";
import Logout from "../../assets/logoutIcon.svg?react";
import SettingsIcon from "../../assets/SettingsIcon.svg?react";

interface NavItem {
    icon: JSX.Element;
    text: string;
    link?: string;
    action?: () => void;
}

export const navItems: NavItem[] = [
    {
        icon: <ModelsIcon />,
        text: "Models",
        link: "/models",
    },
    {
        icon: <DatasetsIcon />,
        text: "Datasets",
        link: "/datasets",
    },
    {
        icon: <EvaluationsIcon />,
        text: "Evaluations",
        link: "/evaluations",
    },
    {
        icon: <ResultsIcon />,
        text: "Overview",
        link: "/overview",
    },
    {
        icon: <CommunityIcon />,
        text: "Community",
        link: "/community",
    },
    {
        icon: <SettingsIcon />,
        text: "Settings",
    },
    {
        icon: <Logout fill="white" />,
        text: "Logout",
        link: "/logout",
    },
];
