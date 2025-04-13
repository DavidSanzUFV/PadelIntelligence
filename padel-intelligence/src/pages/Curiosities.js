import React, { useEffect, useState } from "react";
import CuriosityCard from "../components/CuriosityCard";
import "../styles/Curiosities.css";

const transformCuriosities = (data) => {
  const transformed = {
    "Rankings & Player Profiles": [],
    "Playing Style & Tactics": [],
    "Shot Frequency": [],
    "Effectiveness": [],
    "Serve & Return": []
  };

  const descriptions = {
    "Nationality Ranking": "The most represented countries on tour this season.",
    "Racket Brand Usage": "Top brands used by pro players this year.",
    "Most Wins": "Player with the most matches won this season.",
    "Most Partner Changes": "Player who played with the most different partners.",
    "Side Switchers": "Players who played both left and right sides during the year.",
    "Main Draw Gender Ratio": "Proportion of men and women in main draws in 2024.",
    "Cross vs Parallel": "Top 3 players with highest % of cross-court shots.",
    "Lob to Net Gain %": "Top 3 players who recover net after lob.",
    "Lob Outcomes": "Top 3 players with highest smash-to-lob ratio.",
    "Lobs per Point": "Top 3 players with highest avg of lobs per match.",
    "Total Lobs This Season": "Total number of lobs in the season.",
    "Lob Usage %": "Top 3 players with highest lob usage %. ",
    "Avg of Winners of Viborejas per match": "Top 3 players with most vibora winners per match.",
    "Smash Defenses": "% of smashes defended successfully this season.",
    "Court Exits": "Top 3 players with most smash-defense exits.",
    "1st vs 2nd Serve": "Top 3 players with highest % of 1st serves.",
    "Returns: Lob vs Low": "Top 3 players with highest lob return %.",
    "Return Errors": "Top 3 players with most return error %."
  };

  const icons = {
    "Nationality Ranking": "📊",
    "Racket Brand Usage": "🥎",
    "Most Wins": "🏆",
    "Most Partner Changes": "💔",
    "Side Switchers": "🔁",
    "Main Draw Gender Ratio": "🚻",
    "Cross vs Parallel": "🧭",
    "Lob to Net Gain %": "🎯",
    "Lob Outcomes": "🌀",
    "Lobs per Point": "🌫️",
    "Total Lobs This Season": "📈",
    "Lob Usage %": "🔢",
    "Avg of Winners of Viborejas per match": "💥",
    "Smash Defenses": "🛡️",
    "Court Exits": "🚪",
    "1st vs 2nd Serve": "🎯",
    "Returns: Lob vs Low": "🆙",
    "Return Errors": "❌"
  };

  const percentageTitles = [
    "Main Draw Gender Ratio",
    "Cross vs Parallel",
    "Lob to Net Gain %",
    "Smash Percentage",
    "Lob Usage %",
    "1st vs 2nd Serve",
    "Returns: Lob vs Low",
    "Return Errors"
  ];
  
  const isPercentageTitle = (title) => percentageTitles.includes(title);
  
  for (const [category, items] of Object.entries(data)) {
    for (const [title, facts] of Object.entries(items)) {
      const entry = {
        title,
        icon: icons[title] || "📌",
        description: descriptions[title] || "",
        facts: Array.isArray(facts)
          ? facts.map((f, i) => {
              const medal = ["🥇", "🥈", "🥉"][i] || "🏅";
  
              // 🧠 Si ya es string como "54% Men / 46% Women"
              if (typeof f === "string") return `${medal} ${f}`;
  
              // 🧠 Si es un objeto tipo { player: ..., value: ... }
              if (typeof f === "object" && f !== null) {
                const label =
                  f.player || f.nationality || f.brand || "Item";
                const value = Object.values(f).find(v => typeof v === "number");
  
                if (value !== undefined) {
                  let displayValue;

                  if (["Returns: Lob vs Low", "Lob Usage %"].includes(title)) {
                    displayValue = (value * 100).toFixed(2);
                  } else {
                    displayValue = value.toFixed(2);
                  }
  
                  const suffix = isPercentageTitle(title) ? "%" : "";
                  return `${medal} ${label} (${displayValue}${suffix})`;
                }
  
                // Fallback si no hay número
                const fallback = Object.values(f)
                  .filter(v => typeof v === "string" || typeof v === "number")
                  .slice(1)
                  .join(", ");
                return `${medal} ${label} (${fallback})`;
              }
  
              return `${medal} ${String(f)}`;
            })
          : [`🥇 ${String(facts)}`]
      };
  
      if (transformed[category]) {
        transformed[category].push(entry);
      }
    }
  }
  return transformed;
};

const Curiosities = () => {
  const [curiositiesData, setCuriositiesData] = useState(null);
  const [activeTab, setActiveTab] = useState("Rankings & Player Profiles");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/curiosities")
      .then((res) => res.json())
      .then((data) => {
        const transformed = transformCuriosities(data);
        setCuriositiesData(transformed);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading curiosities:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="curiosities-container">Loading...</div>;
  if (!curiositiesData) return <div className="curiosities-container">No data</div>;

  return (
    <div className="curiosities-container">
      <h1 className="curiosities-title">SEASON CURIOSITIES</h1>
      <p className="curiosities-subtitle">
        Discover surprising facts and quirky moments from this season.
      </p>

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

      <div className="curiosities-grid">
        {curiositiesData[activeTab].map((item, idx) => (
          <CuriosityCard key={idx} {...item} />
        ))}
      </div>
    </div>
  );
};

export default Curiosities;
