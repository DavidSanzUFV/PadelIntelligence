import React, { useState } from "react";
import "../styles/Prediction.css";

// Background image
import backgroundImage from "../assets/fondohome.jpg";
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

  // Opciones para equipos
  const teamOptions = [
    "Arturo Coello Manso/Agustín Tapia",
    "Juan Lebrón Chincoa/Alejandro Galán Romo"
  ];

  // Estilo del fondo
  const containerStyle = {
    background: `
      linear-gradient(rgba(17,24,39, 0.6), rgba(17,24,39, 0.6)),
      url(${backgroundImage}) center center / cover no-repeat
    `
  };

  // Objeto de mapeo para convertir puntos en formato de tenis a valores internos
  const tennisScoreMap = {
    "0": 0,
    "15": 1,
    "30": 2,
    "40": 3,
    "Adv": 4
  };

  const handlePredict = () => {
    // Construir el objeto de request usando la conversión
    const requestData = {
      t1_points: tennisScoreMap[pointsT1],
      t2_points: tennisScoreMap[pointsT2],
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
        if (data.prediction_output) {
          setPredictionOutput(data.prediction_output);
        } else if (data.error) {
          setPredictionOutput("Error: " + data.error);
        }
      })
      .catch((error) => {
        setIsLoading(false);
        setPredictionOutput("Network error: " + error);
      });
  };

  return (
    <div className="prediction-container" style={containerStyle}>
      <h1 className="prediction-title">SCOREBOARD</h1>

      <div className="prediction-instructions">
        <p>
          Enter the current match result by specifying the teams that are playing and the points, games, and sets currently in progress.
          If you click on <b>PREDICT</b>, you will receive key information to help you analyze the match’s progress and foresee potential outcomes.
        </p>
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
        <div className="team-box">
          <img src={coupleImg} alt="Couple Icon" className="couple-image" />
          <div className="team-text">
            <label className="team-label">Team 1</label>
            <input
              list="team1-list"
              className="team-select"
              value={team1}
              onChange={(e) => setTeam1(e.target.value)}
              placeholder="Type or select..."
            />
            <datalist id="team1-list">
              {teamOptions.map((opt) => (
                <option key={opt} value={opt} />
              ))}
            </datalist>
          </div>
        </div>

        <div className="team-box">
          <img src={coupleImg} alt="Couple Icon" className="couple-image" />
          <div className="team-text">
            <label className="team-label">Team 2</label>
            <input
              list="team2-list"
              className="team-select"
              value={team2}
              onChange={(e) => setTeam2(e.target.value)}
              placeholder="Type or select..."
            />
            <datalist id="team2-list">
              {teamOptions.map((opt) => (
                <option key={opt} value={opt} />
              ))}
            </datalist>
          </div>
        </div>
      </div>

      {/* Estadísticas para Team 1 */}
      <div className="row-stats">
        <div className="icon-slot">
          {serving === "team1" && <img src={ballImg} alt="Ball" className="serving-ball" />}
        </div>
        <div className="stats-box">
          <label className="stats-label">POINTS</label>
          <select
            className="stats-input"
            value={pointsT1}
            onChange={(e) => setPointsT1(e.target.value)}
          >
            <option value="0">0</option>
            <option value="15">15</option>
            <option value="30">30</option>
            <option value="40">40</option>
            <option value="Adv">Adv</option>
          </select>
        </div>
        <div className="stats-box">
          <label className="stats-label">GAMES</label>
          <select
            className="stats-input"
            value={gamesT1}
            onChange={(e) => setGamesT1(e.target.value)}
          >
            <option value="0">0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
          </select>
        </div>
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
      </div>

      {/* Estadísticas para Team 2 */}
      <div className="row-stats">
        <div className="icon-slot">
          {serving === "team2" && <img src={ballImg} alt="Ball" className="serving-ball" />}
        </div>
        <div className="stats-box">
          <label className="stats-label">POINTS</label>
          <select
            className="stats-input"
            value={pointsT2}
            onChange={(e) => setPointsT2(e.target.value)}
          >
            <option value="0">0</option>
            <option value="15">15</option>
            <option value="30">30</option>
            <option value="40">40</option>
            <option value="Adv">Adv</option>
          </select>
        </div>
        <div className="stats-box">
          <label className="stats-label">GAMES</label>
          <select
            className="stats-input"
            value={gamesT2}
            onChange={(e) => setGamesT2(e.target.value)}
          >
            <option value="0">0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
          </select>
        </div>
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
      </div>

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
  );
};

export default Prediction;


