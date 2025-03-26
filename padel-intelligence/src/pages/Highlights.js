import React from "react";
import HighlightCard from "../components/HighlightCard";
import "../styles/Highlights.css";
import { FaSnowflake, FaCloud, FaDoorOpen, FaRunning } from "react-icons/fa";
import { GiTennisRacket, GiClick } from "react-icons/gi";
import { GiFlame, GiPathDistance, GiPunch } from "react-icons/gi";

const seasonSummaryTop = [
  {
    icon: <FaSnowflake className="highlight-icon" />,
    title: "Biggest Nevera of the Year",
    player: "Lebrón & Galán vs Coello & Tapia",
    value: "Biggest Nevera of the Year",
    location: "Madrid Master Final",
  },
  {
    icon: <GiClick className="highlight-icon" />,
    title: "Most Shots in a Match",
    player: "Chingotto & Navarro vs Sánchez & Gutiérrez",
    value: "Most Shots in a Match",
    location: "Barcelona Open",
  },
  {
    icon: <FaCloud className="highlight-icon" />,
    title: "Most Lobs in a Match",
    player: "Bela & Tello vs Lebrón & Galán",
    value: "Most Lobs in a Match",
    location: "Buenos Aires P1",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Most Points in a Match",
    player: "Stupa & Di Nenno vs Coello & Tapia",
    value: "Most Points in a Match",
    location: "Málaga P1",
  },
];

const seasonSummaryExtra = [
  {
    icon: <FaDoorOpen className="highlight-icon" />,
    title: "Most Door Exits per Match",
    player: "Coello & Tapia vs Galán & Lebrón",
    value: "Most Door Exits per Match",
    location: "Sevilla Open",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Most Smashes in a Match",
    player: "Coello & Tapia vs Chingotto & Navarro",
    value: "Most Smashes in a Match",
    location: "Roma Major",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Fewest Smashes in a Match",
    player: "Bela & Yanguas vs Sánchez & Gutiérrez",
    value: "Fewest Smashes in a Match",
    location: "Santander Open",
  },
  {
    icon: <FaRunning className="highlight-icon" />,
    title: "Fewest Unforced Errors",
    player: "Stupa & Di Nenno vs Tello & Ruiz",
    value: "Fewest Unforced Errors",
    location: "Vigo P1",
  },
];

const intenseMatches = [
  {
    icon: <GiFlame className="highlight-icon" />,
    title: "Most Repeated Matchup",
    player: "Galán & Lebrón vs Coello & Tapia",
    value: "Played 6 times this season",
    location: "Various Tournaments",
  },
  {
    icon: <GiPathDistance className="highlight-icon" />,
    title: "Most Long Points Played",
    player: "Galán & Lebrón vs Coello & Tapia",
    value: "238 Long Points",
    location: "Roma Major",
  },
  {
    icon: <GiTennisRacket className="highlight-icon" />,
    title: "Most Winners in a Match",
    player: "Coello & Tapia vs Stupa & Di Nenno",
    value: "182 Winners",
    location: "Madrid P1",
  },
  {
    icon: <GiPunch className="highlight-icon" />,
    title: "Most Forced Errors in a Match",
    player: "Galán & Lebrón vs Coello & Tapia",
    value: "76 Forced Errors",
    location: "Valencia P1",
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
      <div className="highlights-intense">
        <h2 className="intense-title">🔥 MOST INTENSE MATCHES</h2>
        <p className="intense-subtitle">
          Discover the fiercest battles and the most spectacular duels of the season.
        </p>
      </div>
      <div className="highlights-grid-3">
        {intenseMatches.map((item, idx) => (
          <HighlightCard key={idx} {...item} isIntense={true} />
        ))}
      </div>

    </div>
  );
};

export default Highlights;
