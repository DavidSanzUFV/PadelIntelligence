import React, { useEffect, useState } from "react";
import HighlightCard from "../components/HighlightCard";
import "../styles/Highlights.css";
import {
  FaSnowflake, FaCloud, FaDoorOpen, FaRunning
} from "react-icons/fa";
import {
  GiTennisRacket, GiClick, GiFlame, GiPathDistance, GiPunch
} from "react-icons/gi";

// 🎯 Mapeo de iconos por título
const iconMap = {
  "Biggest Nevera of the Year": <FaSnowflake className="highlight-icon" />,
  "Most Shots in a Match": <GiClick className="highlight-icon" />,
  "Most Lobs in a Match": <FaCloud className="highlight-icon" />,
  "Most Points in a Match": <GiTennisRacket className="highlight-icon" />,
  "Most Door Exits per Match": <FaDoorOpen className="highlight-icon" />,
  "Most Smashes in a Match": <GiTennisRacket className="highlight-icon" />,
  "Fewest Smashes in a Match": <GiTennisRacket className="highlight-icon" />,
  "Fewest Unforced Errors": <FaRunning className="highlight-icon" />,
  "Most Repeated Matchup": <GiFlame className="highlight-icon" />,
  "Most Long Points Played": <GiPathDistance className="highlight-icon" />,
  "Most Winners in a Match": <GiTennisRacket className="highlight-icon" />,
  "Most Forced Errors in a Match": <GiPunch className="highlight-icon" />
};

const Highlights = () => {
  const [highlights, setHighlights] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/highlights")
      .then(res => res.json())
      .then(data => setHighlights(data))
      .catch(err => console.error("Error loading highlights", err));
  }, []);

  const top = highlights.slice(0, 4);
  const extra = highlights.slice(4, 8);
  const intense = highlights.slice(8, 12);

  return (
    <div className="highlights-container">
      <h1 className="highlights-title">SEASON HIGHLIGHTS</h1>
      <p className="highlights-subtitle">
        Explore the most exciting moments and standout stats of the season.
      </p>

      <div className="highlights-grid">
        {top.map((item, idx) => (
          <HighlightCard
            key={idx}
            icon={iconMap[item.title]}
            {...item}
          />
        ))}
      </div>
      <div className="highlights-intense">
        <h2 className="intense-title">🔥 MOST INTENSE MATCHES</h2>
        <p className="intense-subtitle">
          Discover the fiercest battles and the most spectacular duels of the season.
        </p>
      </div>

      <div className="highlights-grid-3">
        {intense.map((item, idx) => (
          <HighlightCard
            key={idx}
            icon={iconMap[item.title]}
            {...item}
            isIntense={true}
          />
        ))}
      </div>
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
        {extra.map((item, idx) => (
          <HighlightCard
            key={idx}
            icon={iconMap[item.title]}
            {...item}
          />
        ))}
      </div>
    </div>
  );
};

export default Highlights;
