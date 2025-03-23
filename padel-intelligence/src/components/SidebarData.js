import React from "react";
import * as AiIcons from "react-icons/ai";
import * as FaIcons from "react-icons/fa";
import * as IoIcons from "react-icons/io";
import * as MdIcons from "react-icons/md";
import * as GiIcons from "react-icons/gi";

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
  {
    title: "Highlights",
    path: "/highlights",
    icon: <MdIcons.MdStars />, // Estrella para representar momentos destacados
    cName: "nav-text",
  },
  {
    title: "Curiosities",
    path: "/curiosities",
    icon: <GiIcons.GiMagnifyingGlass />, // Lupa para representar descubrimientos curiosos
    cName: "nav-text",
  },
  {
    title: "Comparator",
    path: "/comparator",
    icon: <MdIcons.MdCompare />, // Icono de comparación
    cName: "nav-text",
  },
];


