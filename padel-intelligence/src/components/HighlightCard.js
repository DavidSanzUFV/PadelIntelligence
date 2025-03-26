import React, { useState } from "react";
import "../styles/Highlights.css";

const HighlightCard = ({ icon, title, valueLong, location, isIntense }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`highlight-card ${isIntense ? "highlight-card-intense" : ""}`}>
      <div className="highlight-icon">{icon}</div>

      <div className="highlight-title">{title}</div>

      {/* Location siempre visible */}
      <div className="highlight-location">{location}</div>

      {/* Texto largo solo si está expandido */}
      {expanded && (
        <div className="highlight-details">
          {valueLong}
        </div>
      )}

      {/* Botón toggle */}
      <div className="highlight-toggle" onClick={() => setExpanded(!expanded)}>
        {expanded ? "🔼 Less" : "🔽 More"}
      </div>
    </div>
  );
};

export default HighlightCard;
