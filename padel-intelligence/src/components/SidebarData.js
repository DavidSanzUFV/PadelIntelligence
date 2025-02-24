import React from "react";
import * as AiIcons from "react-icons/ai";
import * as FaIcons from "react-icons/fa";
import * as IoIcons from "react-icons/io";

export const SidebarData = [
  {
    title: "Home",
    path: "/",
    icon: <AiIcons.AiFillHome />,
    cName: "nav-text",
  },
  {
    title: "Couples",
    path: "/couples",
    icon: <FaIcons.FaUserFriends />,
    cName: "nav-text",
  },
  {
    title: "Prediction",
    path: "/prediction",
    icon: <FaIcons.FaChartLine />,
    cName: "nav-text",
  },
  {
    title: "Statistics",
    path: "/statistics",
    icon: <IoIcons.IoIosStats />,
    cName: "nav-text",
  },
];
