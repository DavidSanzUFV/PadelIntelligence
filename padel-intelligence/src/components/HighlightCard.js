import React from "react";
import "../styles/Highlights.css";

const HighlightCard = ({ icon, value, player, match, location, isIntense }) => {
  return (
    <div className={`highlight-card ${isIntense ? 'highlight-card-intense' : ''}`}>
      <div className="highlight-icon">{icon}</div>
      <div className="highlight-value">{value}</div>
      <div className="highlight-player">{player}</div>
      <div className="highlight-match">{match}</div>
      <div className="highlight-location">{location}</div>
    </div>
  );
};

export default HighlightCard;
