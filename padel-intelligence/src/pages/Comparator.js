import React, { useEffect, useState } from "react";
import "../styles/Statistics.css";
import "../styles/Comparator.css";
import RadarChartComparison from "../components/RadarChartComparison";

const Comparator = () => {
  const [players, setPlayers] = useState([]);
  const [player1, setPlayer1] = useState(null);
  const [player2, setPlayer2] = useState(null);
  const [query1, setQuery1] = useState("");
  const [query2, setQuery2] = useState("");
  const [benchmarkMax, setBenchmarkMax] = useState(null);

  useEffect(() => {
    fetch("/players")
      .then((res) => res.json())
      .then((data) => {
        const uniquePlayers = {};
        data.forEach((player) => {
          const key = player.player;
          if (!uniquePlayers[key]) {
            uniquePlayers[key] = { ...player, side: new Set([player.side]) };
          } else {
            uniquePlayers[key].side.add(player.side);
          }
        });

        const formattedPlayers = Object.values(uniquePlayers).map((player) => ({
          ...player,
          side: player.side.size > 1
            ? "Both sides"
            : player.side.has("Right")
            ? "Right side"
            : "Left side"
        }));

        setPlayers(formattedPlayers);
      });
  }, []);

  useEffect(() => {
    fetch("/benchmark_max")
      .then((res) => res.json())
      .then((data) => setBenchmarkMax(data))
      .catch((err) => console.error("❌ Error fetching benchmark max:", err));
  }, []);
  
  const findPlayer = async (query, setPlayer) => {
    const basicInfo = players.find((p) => p.player.toLowerCase().includes(query.toLowerCase()));
    if (!basicInfo) return;

    try {
      const res = await fetch(`/player_stats/${basicInfo.player}`);
      const extraInfo = await res.json();
      setPlayer({ ...basicInfo, ...extraInfo });
    } catch (error) {
      console.error("Error fetching advanced stats:", error);
      setPlayer(basicInfo); // fallback
    }
  };

  const PlayerCard = ({ player }) => {
    if (!player) return null;

    const getFlagURL = (nationality) => {
      const codes = {
        Argentina: "ar", Belgium: "be", Brazil: "br", Chile: "cl", Egypt: "eg",
        Finland: "fi", France: "fr", Italy: "it", Kuwait: "kw", Mexico: "mx",
        Netherlands: "nl", Paraguay: "py", Portugal: "pt", Qatar: "qa", Russia: "ru",
        Saudi_Arabia: "sa", Spain: "es", Sweden: "se", USA: "us", Venezuela: "ve"
      };
      return `https://flagcdn.com/w80/${codes[nationality]?.toLowerCase()}.png`;
    };

    const getBrandLogo = (brand) => {
      const formatted = brand?.normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/\s+/g, "")
        .replace(/[^a-zA-Z0-9]/g, "")
        .toLowerCase();
      return `/assets/brands/${formatted}.png`;
    };

    return (
      <div className="player-card">
        <div className="player-name">{player.player}</div>
        <div className="player-photo-container">
          <img src={getFlagURL(player.nationality)} alt="Flag" className="player-flag" />
          <img src={player.photo} alt="player" className="player-photo" />
          <img src={getBrandLogo(player.brand)} alt={player.brand} className="brand-logo" />
        </div>
        <div className="player-details">
          <span>{player.hand === "Right" ? "Right-handed" : "Left-handed"}</span>
          <span>{player.side}</span>
        </div>
      </div>
    );
  };

  const getHighlightClass = (val1, val2) => {
    const n1 = parseFloat(val1);
    const n2 = parseFloat(val2);
    if (isNaN(n1) || isNaN(n2)) return ["", ""];
    if (n1 > n2) return ["highlight-winner", "highlight-loser"];
    if (n1 < n2) return ["highlight-loser", "highlight-winner"];
    return ["highlight-draw", "highlight-draw"];
  };
  
  const renderRow = (label, key, format = (v) => `${v}%`) => {
    const [p1Class, p2Class] = getHighlightClass(player1?.[key], player2?.[key]);
    return (
    <tr>
      <td>
        <span className={p1Class}>
          {player1?.[key] !== undefined ? format(player1[key]) : "-"}
        </span>
      </td>
      <td className="field-label">{label}</td>
      <td>
        <span className={p2Class}>
          {player2?.[key] !== undefined ? format(player2[key]) : "-"}
        </span>
      </td>
    </tr>
    );
  };

  return (
    <div className="statistics-container-comparator">
      <h1 className="title">PLAYER COMPARATOR</h1>
      <p className="subtitle">Search and compare two players side by side.</p>

      <div className="filters-container">
        <input
          type="text"
          placeholder="Search player 1..."
          value={query1}
          onChange={(e) => {
            const value = e.target.value;
            setQuery1(value);
            findPlayer(value, setPlayer1);
          }}
        />
        <input
          type="text"
          placeholder="Search player 2..."
          value={query2}
          onChange={(e) => {
            const value = e.target.value;
            setQuery2(value);
            findPlayer(value, setPlayer2);
          }}
        />
      </div>

      {player1 && player2 && (
        
        <>
   <div className="players-grid">
      <PlayerCard player={player1} />
      <PlayerCard player={player2} />
    </div>

    <div className="radar-chart-wrapper">
      <RadarChartComparison
        player1={player1}
        player2={player2}
        benchmarkMax={benchmarkMax}
      />
    </div>
          <div className="comparison-block">
            <h3 className="comparison-title">TOURNAMENTS</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("Tournaments Played", "tournaments_played", (v) => v)}
                  {renderRow("Matches Played", "matches_played", (v) => v)}
                  {renderRow("Win Rate", "win_rate")}
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparison-block">
            <h3 className="comparison-title">SERVES</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("% First Serves", "percentage_1st_serves")}
                  {renderRow("% Service Games Won", "percentage_service_games_won")}
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparison-block">
            <h3 className="comparison-title">TACTICS</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("% Cross-court Shots", "percentage_cross")}
                  {renderRow("% Parallel Shots", "percentage_parallel")}
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparison-block">
            <h3 className="comparison-title">RETURNS</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("% Lob Returns", "percentage_lobbed_returns")}
                  {renderRow("% Flat Returns", "percentage_flat_returns")}
                  {renderRow("% Error Returns", "percentage_return_errors")}
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparison-block">
            <h3 className="comparison-title">AERIAL GAME</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("Lobs Received per Match", "lobs_received_per_match", (v) => v)}
                  {renderRow("% Smashes from Lobs", "percentage_smashes_from_lobs")}
                  {renderRow("% Rulos from Lobs", "percentage_rulos_from_lobs")}
                  {renderRow("% Viborejas from Lobs", "percentage_viborejas_from_lobs")}
                  {renderRow("% Bajadas from Lobs", "percentage_bajadas_from_lobs")}
                  {renderRow("% Winners from Lobs Received", "winners_from_lobs")}
                </tbody>
              </table>
            </div>
          </div>

          <div className="comparison-block">
            <h3 className="comparison-title">DEFENSE</h3>
            <div className="comparison-box">
              <table className="comparison-table">
                <tbody>
                  {renderRow("Number of Outside recoveries in the season", "outside_recoveries", (v) => v)}
                  {renderRow("Lobs Played per Match", "lobs_played_per_match", (v) => v)}
                  {renderRow("% Net Recovery with Lob", "net_recovery_with_lob", (v) => `${parseFloat(v).toFixed(2)}%`)}
                  {renderRow("Number of Unforced Errors per Match", "unforced_errors_per_match", (v) => v)}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Comparator;

