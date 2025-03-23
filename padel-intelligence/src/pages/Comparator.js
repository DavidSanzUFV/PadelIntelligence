import React, { useEffect, useState } from "react";
import "../styles/Statistics.css"; // reutilizamos estilos existentes
import "../styles/Comparator.css"; // reutilizamos estilos existentes

const Comparator = () => {
  const [players, setPlayers] = useState([]);
  const [player1, setPlayer1] = useState(null);
  const [player2, setPlayer2] = useState(null);
  const [query1, setQuery1] = useState("");
  const [query2, setQuery2] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/players")
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

  const findPlayer = (query) =>
    players.find((p) => p.player.toLowerCase().includes(query.toLowerCase()));

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
      const formatted = brand?.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
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
/*
  const renderComparisonSection = (title, fields) => (
    <div className="comparison-wrapper">
      <h3 className="comparison-title">{title}</h3>
      <div className="comparison-box">
        <table className="comparison-table">
          <tbody>
            {fields.map(({ label, key, unit }) => (
              <tr key={key}>
                <td>{player1?.[key] ? `${player1[key]}${unit}` : "-"}</td>
                <td className="field-label">{label}</td>
                <td>{player2?.[key] ? `${player2[key]}${unit}` : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
  */
  return (
    <div className="statistics-container-comparator">
      <h1 className="title">PLAYER COMPARATOR</h1>
      <p className="subtitle">Search and compare two players side by side.</p>

      {/* Buscadores */}
      <div className="filters-container">
        <input
          type="text"
          placeholder="Search player 1..."
          value={query1}
          onChange={(e) => {
            setQuery1(e.target.value);
            const found = findPlayer(e.target.value);
            if (found) setPlayer1(found);
          }}
        />
        <input
          type="text"
          placeholder="Search player 2..."
          value={query2}
          onChange={(e) => {
            setQuery2(e.target.value);
            const found = findPlayer(e.target.value);
            if (found) setPlayer2(found);
          }}
        />
      </div>

      {/* Tarjetas comparativas */}
<div className="players-grid">
  <PlayerCard player={player1} />
  <PlayerCard player={player2} />

  {player1 && player2 && (
    <>
<div className="comparison-block">
  <h3 className="comparison-title">TOURNAMENTS</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.tournaments_played ?? "-"}</td>
          <td className="field-label">Tournaments Played</td>
          <td>{player2?.tournaments_played ?? "-"}</td>
        </tr>
        <tr>
          <td>{player1?.matches ?? "-"}</td>
          <td className="field-label">Matches Played</td>
          <td>{player2?.matches ?? "-"}</td>
        </tr>
        <tr>
          <td>{player1?.win_rate ? `${player1.win_rate}%` : "-"}</td>
          <td className="field-label">Win Rate</td>
          <td>{player2?.win_rate ? `${player2.win_rate}%` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div className="comparison-block">
  <h3 className="comparison-title">SERVES</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.first_serve_percentage ? `${player1.first_serve_percentage}%` : "-"}</td>
          <td className="field-label">% First Serves</td>
          <td>{player2?.first_serve_percentage ? `${player2.first_serve_percentage}%` : "-"}</td>
        </tr>
        <tr>
          <td>{player1?.service_games_won ? `${player1.service_games_won}%` : "-"}</td>
          <td className="field-label">% Service Games Won</td>
          <td>{player2?.service_games_won ? `${player2.service_games_won}%` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div className="comparison-block">
  <h3 className="comparison-title">TACTICS</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.cross_vs_parallel ? `${player1.cross_vs_parallel}` : "-"}</td>
          <td className="field-label">% Cross-court vs Down-the-line Shots</td>
          <td>{player2?.cross_vs_parallel ? `${player2.cross_vs_parallel}` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div className="comparison-block">
  <h3 className="comparison-title">RETURNS</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.return_lobs ? `${player1.return_lobs}%` : "-"}</td>
          <td className="field-label">% Return Lobs</td>
          <td>{player2?.return_lobs ? `${player2.return_lobs}%` : "-"}</td>
        </tr>
        <tr>
          <td>{player1?.return_low ? `${player1.return_low}%` : "-"}</td>
          <td className="field-label">% Low Returns</td>
          <td>{player2?.return_low ? `${player2.return_low}%` : "-"}</td>
        </tr>
        <tr>
          <td>{player1?.return_errors ? `${player1.return_errors}%` : "-"}</td>
          <td className="field-label">% Return Errors</td>
          <td>{player2?.return_errors ? `${player2.return_errors}%` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div className="comparison-block">
  <h3 className="comparison-title">AERIAL GAME</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.lobs_received_per_match ?? "-"}</td>
          <td className="field-label">Lobs Received per Match</td>
          <td>{player2?.lobs_received_per_match ?? "-"}</td>
        </tr>
        <tr>
          <td>{player1?.lob_response_distribution ?? "-"}</td>
          <td className="field-label">Response to Lobs (% smashes, rulos, víboras/bandejas, bajadas)</td>
          <td>{player2?.lob_response_distribution ?? "-"}</td>
        </tr>
        <tr>
          <td>{player1?.winners_from_lobs ? `${player1.winners_from_lobs}%` : "-"}</td>
          <td className="field-label">% Winners from Lobs Received</td>
          <td>{player2?.winners_from_lobs ? `${player2.winners_from_lobs}%` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<div className="comparison-block">
  <h3 className="comparison-title">DEFENSE</h3>
  <div className="comparison-box">
    <table className="comparison-table">
      <tbody>
        <tr>
          <td>{player1?.smash_recovery_percentage ? `${player1.smash_recovery_percentage}%` : "-"}</td>
          <td className="field-label">% Smashes Recovered</td>
          <td>{player2?.smash_recovery_percentage ? `${player2.smash_recovery_percentage}%` : "-"}</td>
        </tr>
        <tr>
          <td>{player1?.lobs_played_per_point ?? "-"}</td>
          <td className="field-label">Lobs Played per Point</td>
          <td>{player2?.lobs_played_per_point ?? "-"}</td>
        </tr>
        <tr>
          <td>{player1?.net_recovery_with_lob ? `${player1.net_recovery_with_lob}%` : "-"}</td>
          <td className="field-label">% Net Recovery with Lob</td>
          <td>{player2?.net_recovery_with_lob ? `${player2.net_recovery_with_lob}%` : "-"}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
    </>
  )}
</div>


          {/* Más secciones futuras */}
        </div>
      )}

export default Comparator;
