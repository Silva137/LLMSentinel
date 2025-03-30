import { JSX } from "react";
import { Logout } from "pixelarticons/fonts/react";

import ModelsIcon from "../../assets/modelsIcon.svg?react";
import DatasetsIcon from "../../assets/datasetsIcon.svg?react";
import EvaluationsIcon from "../../assets/evaluationsIcon.svg?react";
import ResultsIcon from "../../assets/resultsIcon.svg?react";
import LeaderboardIcon from "../../assets/leaderboardIcon.svg?react";

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
        icon: <LeaderboardIcon />,
        text: "Leaderboard",
        link: "/leaderboard",
    },
    {
        icon: <Logout size={24} fill="white" />,
        text: "Logout",
        link: "/logout",
    },
];
