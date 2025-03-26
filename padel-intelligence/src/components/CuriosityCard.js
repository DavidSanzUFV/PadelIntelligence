import React, { useState } from "react";
import "../styles/CuriosityCard.css";

const CuriosityCard = ({ icon, title, description, facts }) => {
  const [flipped, setFlipped] = useState(false);

  const handleFlip = () => {
    setFlipped(!flipped);
  };

  const renderFacts = () => {
    if (!facts || facts.length === 0) return null;

    return facts.map((fact, idx) => (
      <div key={idx} className="medal-line">
        <span className="fact">{fact}</span>
      </div>
    ));
  };

  return (
    <div className={`curiosity-card ${flipped ? "flipped" : ""}`} onClick={handleFlip}>
      <div className="curiosity-card-inner">
        <div className="curiosity-card-front">
          <div className="curiosity-icon">{icon}</div>
          <div className="curiosity-content">
            <div className="curiosity-title">{title}</div>
            <div className="curiosity-description">{description}</div>
          </div>
        </div>

        <div className="curiosity-card-back">
          {renderFacts()}
        </div>
      </div>
    </div>
  );
};

export default CuriosityCard;
