import React from "react";
import HighlightCard from "../components/HighlightCard";
import "../styles/Highlights.css";
import { FaSnowflake, FaCloud, FaDoorOpen, FaRunning } from "react-icons/fa";
import { GiTennisRacket, GiClick } from "react-icons/gi";

const seasonSummaryTop = [
  {
    icon: <FaSnowflake className="highlight-icon" />,
    title: "Biggest Nevera of the Year",
    player: "Lebrón & Galán vs Coello & Tapia",
    value: "Biggest Nevera of the Year",
  },
  {
    icon: <GiClick className="highlight-icon" />,
    title: "Most Shots in a Match",
    player: "Chingotto & Navarro vs Sánchez & Gutiérrez",
    value: "Most Shots in a Match",
  },
  {
    icon: <FaCloud className="highlight-icon" />,
    title: "Most Lobs in a Match",
    player: "Bela & Tello vs Lebrón & Galán",
    value: "Most Lobs in a Match",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Most Points in a Match",
    player: "Stupa & Di Nenno vs Coello & Tapia",
    value: "Most Points in a Match",
  },
];


// 📊 SEASON SUMMARY - Extra Highlights
const seasonSummaryExtra = [
  {
    icon: <FaDoorOpen className="highlight-icon" />,
    title: "Most Door Exits per Match",
    player: "Coello & Tapia vs Galán & Lebrón",
    value: "Most Door Exits per Match",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Most Smashes in a Match",
    player: "Coello & Tapia vs Chingotto & Navarro",
    value: "Most Smashes in a Match",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Fewest Smashes in a Match",
    player: "Bela & Yanguas vs Sánchez & Gutiérrez",
    value: "Fewest Smashes in a Match",
  },
  {
    icon: <FaRunning className="highlight-icon" />,
    title: "Fewest Unforced Errors",
    player: "Stupa & Di Nenno vs Tello & Ruiz",
    value: "Fewest Unforced Errors",
  },
];



const Highlights = () => {
  return (
    <div className="highlights-container">
      <h1 className="highlights-title">SEASON HIGHLIGHTS</h1>
      <p className="highlights-subtitle">
        Explore the most exciting moments and standout stats of the season.
      </p>

      <div className="highlights-grid">
        {seasonSummaryTop.map((item, idx) => (
          <HighlightCard key={idx} {...item} />
        ))}
      </div>

      {/* NUEVA SECCIÓN DE ESTADÍSTICAS TOTALES */}
      <div className="highlights-summary">
        <h2 className="summary-title">📊 SEASON SUMMARY</h2>
        <div className="summary-stats">
          <div className="summary-item">
            <span className="summary-number">264</span>
            <span className="summary-label">Total Matches</span>
          </div>
          <div className="summary-item">
            <span className="summary-number">846</span>
            <span className="summary-label">Total Sets Played</span>
          </div>
          <div className="summary-item">
            <span className="summary-number">12,300</span>
            <span className="summary-label">Total Points</span>
          </div>
        </div>
      </div>
      <div className="highlights-grid-2">
        {seasonSummaryExtra.map((item, idx) => (
          <HighlightCard key={idx} {...item} />
        ))}
      </div>
    </div>
  );
};

export default Highlights;
