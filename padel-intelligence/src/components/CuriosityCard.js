import React from "react";
import "../styles/CuriosityCard.css";

const CuriosityCard = ({ icon, title, description }) => {
  return (
    <div className="curiosity-card">
      <div className="curiosity-icon">{icon}</div>
      <div className="curiosity-content">
        <h3 className="curiosity-title">{title}</h3>
        <p className="curiosity-description">{description}</p>
      </div>
    </div>
  );
};

export default CuriosityCard;
