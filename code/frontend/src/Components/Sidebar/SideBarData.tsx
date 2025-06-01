import { JSX } from "react";

import ModelsIcon from "../../assets/modelsIcon.svg?react";
import DatasetsIcon from "../../assets/datasetsIcon.svg?react";
import EvaluationsIcon from "../../assets/evaluationsIcon.svg?react";
import ResultsIcon from "../../assets/resultsIcon.svg?react";
import CommunityIcon from "../../assets/communityIcon.svg?react";
import Logout from "../../assets/logoutIcon.svg?react";

interface NavItem {
    icon: JSX.Element;
    text: string;
    link: string;
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
        text: "Results",
        link: "/results",
    },
    {
        icon: <CommunityIcon />,
        text: "Community",
        link: "/community",
    },
    {
        icon: <Logout fill="white" />,
        text: "Logout",
        link: "/logout",
    },
];
