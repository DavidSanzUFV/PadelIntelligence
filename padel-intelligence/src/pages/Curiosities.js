import React, { useState } from "react";
import CuriosityCard from "../components/CuriosityCard";
import "../styles/Curiosities.css";

const curiositiesData = {
  "Rankings & Player Profiles": [
    {
      icon: "📊",
      title: "Nationality Ranking",
      fact: "TOP 5",
      description: "The most represented countries on tour this season."
    },
    {
      icon: "🥎",
      title: "Racket Brand Usage",
      fact: "TOP 5",
      description: "Top brands used by pro players this year."
    },
    {
      icon: "🏆",
      title: "Most Wins",
      fact: "36",
      description: "Player with the most matches won this season."
    },
    {
      icon: "💔",
      title: "Most Partner Changes",
      fact: "6",
      description: "Javi Leal played with 6 different partners this season."
    },
    {
      icon: "🔁",
      title: "Side Switchers",
      fact: "Multiple",
      description: "Players who played both left and right sides during the year."
    },
    {
      icon: "🚻",
      title: "Main Draw Gender Ratio",
      fact: "63% Men / 37% Women",
      description: "Proportion of men and women in main draws in 2024."
    }
  ],
  "Playing Style & Tactics": [
    {
      icon: "🧭",
      title: "Cross vs Parallel",
      fact: "62% Cross",
      description: "Majority of points played cross-court this season."
    },
    {
      icon: "🎯",
      title: "Lob to Net Gain %",
      fact: "31%",
      description: "How often lobs helped players win the net."
    },
    {
      icon: "🌀",
      title: "Lob Outcomes",
      fact: "Mixed",
      description: "What usually happens after a lob: remate, bandeja, etc."
    }
  ],
  "Shot Frequency": [
    {
      icon: "🌫️",
      title: "Lobs per Point",
      fact: "1.4 avg",
      description: "Average number of lobs per point played."
    },
    {
      icon: "🎾",
      title: "Shot Mix per Point",
      fact: "4 types",
      description: "Smashes, bandejas, rulos and bajadas in each rally."
    },
    {
      icon: "📈",
      title: "Total Lobs This Season",
      fact: "6,830",
      description: "Number of lobs registered during the season."
    },
    {
      icon: "🔢",
      title: "Lob Usage %",
      fact: "28%",
      description: "Percentage of points that include at least one lob."
    }
  ],
  "Effectiveness": [
    {
      icon: "💥",
      title: "Winner % by Shot Type",
      fact: "47%",
      description: "How effective are smashes, rulos, etc. in ending points."
    },
    {
      icon: "🛡️",
      title: "Smash Defenses",
      fact: "18%",
      description: "How often smashes are successfully defended."
    },
    {
      icon: "🚪",
      title: "Court Exits",
      fact: "3.1 per match",
      description: "Average number of exits per match to recover balls."
    }
  ],
  "Serve & Return": [
    {
      icon: "🎯",
      title: "1st vs 2nd Serve",
      fact: "79% / 21%",
      description: "Percentage of points played with first or second serve."
    },
    {
      icon: "🆙",
      title: "Returns: Lob vs Low",
      fact: "42% lobs",
      description: "How players chose to return: lob or drive."
    },
    {
      icon: "❌",
      title: "Return Errors",
      fact: "11%",
      description: "Direct unforced errors made while returning serve."
    }
  ]
};


const Curiosities = () => {
  const [activeTab, setActiveTab] = useState("Rankings & Player Profiles");

  return (
    <div className="curiosities-container">
      <h1 className="curiosities-title">SEASON CURIOSITIES</h1>
      <p className="curiosities-subtitle">
        Discover surprising facts and quirky moments from this season.
      </p>

      {/* Tabs */}
      <div className="curiosities-tabs">
        {Object.keys(curiositiesData).map((category) => (
          <button
            key={category}
            className={`curiosity-tab ${activeTab === category ? "active" : ""}`}
            onClick={() => setActiveTab(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="curiosities-grid">
        {curiositiesData[activeTab].map((item, idx) => (
          <CuriosityCard key={idx} {...item} />
        ))}
      </div>
    </div>
  );
};

export default Curiosities;
