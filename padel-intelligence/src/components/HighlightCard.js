import React from "react";
import "../styles/Highlights.css";

const HighlightCard = ({ icon, value, player, match }) => {
  return (
    <div className="highlight-card">
      <div className="highlight-icon">{icon}</div>
      <div className="highlight-value">{value}</div>
      <div className="highlight-player">{player}</div>
      <div className="highlight-match">{match}</div>
    </div>
  );
};

export default HighlightCard;
