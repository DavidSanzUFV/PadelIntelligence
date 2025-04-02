import React, { useState, useEffect } from "react";
import "../styles/Prediction.css";

import logo from "../assets/logo.png";

// Icons
import servingImg from "../assets/whoisserving.png";
import coupleImg from "../assets/couple.png";
import ballImg from "../assets/bola.png";



const Prediction = () => {
  // Fijamos estas probabilidades:
  const pServe = 0.8;
  const pGamesWonOnServe = 0.7;

  // Quién sirve
  const [serving, setServing] = useState("");

  // Nombres de equipo (opcional)
  const [team1, setTeam1] = useState("");
  const [team2, setTeam2] = useState("");

  // Estadísticas para el equipo 1
  const [pointsT1, setPointsT1] = useState("0");
  const [gamesT1, setGamesT1] = useState("0");
  const [setsT1, setSetsT1] = useState("0");

  // Estadísticas para el equipo 2
  const [pointsT2, setPointsT2] = useState("0");
  const [gamesT2, setGamesT2] = useState("0");
  const [setsT2, setSetsT2] = useState("0");

  // Estados para el panel de predicción y salida
  const [showPanel, setShowPanel] = useState(false);
  const [predictionOutput, setPredictionOutput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [showSuggestionsT1, setShowSuggestionsT1] = useState(false);
  const [showSuggestionsT2, setShowSuggestionsT2] = useState(false);
  
  const [pairs, setPairs] = useState([]);

 // Fetch de parejas al montar el componente
 useEffect(() => {
  fetch("http://127.0.0.1:8000/pairs")
    .then((response) => response.json())
    .then((data) => {
      setPairs(data);
    })
    .catch((error) => console.error("❌ Error fetching pairs:", error));
}, []);


  const handlePredict = () => {
    // Construir el objeto de request usando los valores tal como están en el select
    const requestData = {
      t1_points: pointsT1,   // No convertir a número
      t2_points: pointsT2,   // No convertir a número
      t1_games: parseInt(gamesT1, 10),
      t2_games: parseInt(gamesT2, 10),
      t1_sets: parseInt(setsT1, 10),
      t2_sets: parseInt(setsT2, 10),
      serve: serving === "team1" ? 1 : 2,
      p_serve: pServe,
      p_games_won_on_serve: pGamesWonOnServe
    };
  
    // Mostrar panel e indicar carga
    setShowPanel(true);
    setIsLoading(true);
    setPredictionOutput("Loading...");
   
    // Enviar solicitud POST al endpoint de FastAPI
    fetch("http://127.0.0.1:8000/run_prediction/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    })
      .then((response) => response.json())
      .then((data) => {
        setIsLoading(false);
        if (data.error && data.error[0]) {
          setPredictionOutput("Error: " + data.error[1]);
        } else if (data.game_probability && data.set_probability && data.match_probability) {
          // Mostrar las probabilidades devueltas por el backend
          setPredictionOutput(
            `Game Probability: ${data.game_probability}\n` +
            `Set Probability: ${data.set_probability}\n` +
            `Match Probability: ${data.match_probability}`
          );
        } else {
          setPredictionOutput("Unexpected response format.");
        }
      })
      .catch((error) => {
        setIsLoading(false);
        setPredictionOutput("Network error: " + error);
      });
  };
  
  
  return (
    <>
    <div className="prediction-container">
      <div className="prediction-main-card">
        <div className="info-wrapper">
          <h1 className="prediction-title">
            PREDICT A MATCH
            <span className="info-icon" onClick={() => setShowInfo(!showInfo)}>ℹ️</span>
          </h1>

          {showInfo && (
            <div className="info-box">
              <p>
                Enter the current match result by specifying the teams that are playing and the points, games, and sets currently in progress.
                If you click on <b>PREDICT</b>, you will receive key information to help you analyze the match’s progress and foresee potential outcomes.
              </p>
          </div>
          )}
        </div>

      {/* Quién sirve */}
      <div className="row-serving">
        <div className="serving-box">
          <img src={servingImg} alt="Who is serving" className="serving-image" />
          <label className="serving-label">Who is serving?</label>
          <select
            className="serving-select"
            value={serving}
            onChange={(e) => setServing(e.target.value)}
          >
            <option value="">-- Select --</option>
            <option value="team1">Team 1</option>
            <option value="team2">Team 2</option>
          </select>
        </div>
      </div>

{/* Equipos */}
<div className="row-teams">
  {/* Team 1 */}
  <div className="team-box team-box-relative">
    <img src={coupleImg} alt="Couple Icon" className="couple-image" />
    <div className="team-text autocomplete-wrapper">
      <label className="team-label">Team 1</label>
      <input
        className="team-select"
        type="text"
        value={team1}
        onChange={(e) => {
          setTeam1(e.target.value);
          setShowSuggestionsT1(true);
        }}
        placeholder="Type to search..."
        autoComplete="off"
      />
      {showSuggestionsT1 && team1 && (
        <ul className="autocomplete-list">
          {pairs
            .filter((pair) =>
              `${pair.player1} / ${pair.player2}`
                .toLowerCase()
                .includes(team1.toLowerCase())
            )
            .slice(0, 5)
            .map((pair, index) => (
              <li
                key={index}
                onClick={() => {
                  setTeam1(`${pair.player1} / ${pair.player2}`);
                  setShowSuggestionsT1(false);
                }}
                className="autocomplete-option"
              >
                {pair.player1} / {pair.player2}
              </li>
            ))}
        </ul>
      )}
    </div>
  </div>

  {/* Team 2 */}
  <div className="team-box team-box-relative">
    <img src={coupleImg} alt="Couple Icon" className="couple-image" />
    <div className="team-text autocomplete-wrapper">
      <label className="team-label">Team 2</label>
      <input
        className="team-select"
        type="text"
        value={team2}
        onChange={(e) => {
          setTeam2(e.target.value);
          setShowSuggestionsT2(true);
        }}
        placeholder="Type to search..."
        autoComplete="off"
      />
      {showSuggestionsT2 && team2 && (
        <ul className="autocomplete-list">
          {pairs
            .filter((pair) =>
              `${pair.player1} / ${pair.player2}`
                .toLowerCase()
                .includes(team2.toLowerCase())
            )
            .slice(0, 5)
            .map((pair, index) => (
              <li
                key={index}
                onClick={() => {
                  setTeam2(`${pair.player1} / ${pair.player2}`);
                  setShowSuggestionsT2(false);
                }}
                className="autocomplete-option"
              >
                {pair.player1} / {pair.player2}
              </li>
            ))}
        </ul>
      )}
    </div>
  </div>
</div>

{/* Estadísticas para Team 1 */}
<div className="row-stats">
  <div className="icon-slot">
    {serving === "team1" && <img src={ballImg} alt="Ball" className="serving-ball" />}
  </div>
  
  {/* SET */}
  <div className="stats-box">
    <label className="stats-label">SET</label>
    <select
      className="stats-input"
      value={setsT1}
      onChange={(e) => setSetsT1(e.target.value)}
    >
      <option value="0">0</option>
      <option value="1">1</option>
      <option value="2">2</option>
    </select>
  </div>

  {/* GAMES */}
  <div className="stats-box">
    <label className="stats-label">GAMES</label>
    <select
      className="stats-input"
      value={gamesT1}
      onChange={(e) => setGamesT1(e.target.value)}
    >
      {[...Array(8).keys()].map((game) => (
        <option key={game} value={game}>{game}</option>
      ))}
    </select>
  </div>

  {/* POINTS */}
  <div className="stats-box">
    <label className="stats-label">POINTS</label>
    <select
      className="stats-input"
      value={pointsT1}
      onChange={(e) => setPointsT1(e.target.value)}
    >
      {gamesT1 === "6" && gamesT2 === "6" ? (
        Array.from({ length: 15 }, (_, i) => (
          <option key={i} value={i}>{i}</option>
        ))
      ) : (
        <>
          <option value="0">0</option>
          <option value="15">15</option>
          <option value="30">30</option>
          <option value="40">40</option>
          <option value="Adv">Adv</option>
        </>
      )}
    </select>
  </div>
</div>

{/* Estadísticas para Team 2 */}
<div className="row-stats">
  <div className="icon-slot">
    {serving === "team2" && <img src={ballImg} alt="Ball" className="serving-ball" />}
  </div>

  {/* SET */}
  <div className="stats-box">
    <label className="stats-label">SET</label>
    <select
      className="stats-input"
      value={setsT2}
      onChange={(e) => setSetsT2(e.target.value)}
    >
      <option value="0">0</option>
      <option value="1">1</option>
      <option value="2">2</option>
    </select>
  </div>

  {/* GAMES */}
  <div className="stats-box">
    <label className="stats-label">GAMES</label>
    <select
      className="stats-input"
      value={gamesT2}
      onChange={(e) => setGamesT2(e.target.value)}
    >
      {[...Array(8).keys()].map((game) => (
        <option key={game} value={game}>{game}</option>
      ))}
    </select>
  </div>

  {/* POINTS */}
  <div className="stats-box">
    <label className="stats-label">POINTS</label>
    <select
      className="stats-input"
      value={pointsT2}
      onChange={(e) => setPointsT2(e.target.value)}
    >
      {gamesT1 === "6" && gamesT2 === "6" ? (
        Array.from({ length: 15 }, (_, i) => (
          <option key={i} value={i}>{i}</option>
        ))
      ) : (
        <>
          <option value="0">0</option>
          <option value="15">15</option>
          <option value="30">30</option>
          <option value="40">40</option>
          <option value="Adv">Adv</option>
        </>
      )}
    </select>
  </div>
</div>

{/* BOTÓN DE PREDICCIÓN */}
<button className="predict-button" onClick={handlePredict}>
  PREDICT
</button>

      {/* Overlay and Prediction Panel */}
      {showPanel && (
        <>
          <div className="prediction-overlay" onClick={() => setShowPanel(false)} />
          <div className="prediction-panel">
            <h2>
              ¡Prediction Generated!{" "}
              <span role="img" aria-label="crystal-ball">
                🔮
              </span>
            </h2>
            {isLoading ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <p style={{ fontSize: "1.4rem", fontWeight: "bold" }}>
                  Loading...
                </p>
                <img
                  src={logo}
                  alt="loading"
                  style={{ width: "120px", marginTop: "10px", filter: "brightness(0) invert(1)" }}
                />
              </div>
            ) : (
              <pre style={{ textAlign: "left" }}>{predictionOutput}</pre>
            )}
            <button className="close-panel" onClick={() => setShowPanel(false)}>
              Close
            </button>
          </div>
        </>
      )}
      </div>
    </div>
    </>
  );
};

export default Prediction;