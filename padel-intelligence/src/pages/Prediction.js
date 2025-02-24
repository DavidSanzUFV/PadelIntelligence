import React, { useState } from "react";
import "../styles/Prediction.css";

// Imagen de fondo
import backgroundImage from "../assets/fondohome.jpg";

// Íconos
import servingImg from "../assets/whoisserving.png";
import coupleImg from "../assets/couple.png";
import ballImg from "../assets/bola.png";

const Prediction = () => {
  // Estados para el formulario
  const [serving, setServing] = useState("");
  const [team1, setTeam1] = useState("");
  const [team2, setTeam2] = useState("");

  // Puntos, Games, Sets T1
  const [pointsT1, setPointsT1] = useState("");
  const [gamesT1, setGamesT1] = useState("");
  const [setsT1, setSetsT1] = useState("");

  // Puntos, Games, Sets T2
  const [pointsT2, setPointsT2] = useState("");
  const [gamesT2, setGamesT2] = useState("");
  const [setsT2, setSetsT2] = useState("");

  // Estado para mostrar/ocultar el panel de predicción
  const [showPanel, setShowPanel] = useState(false);

  // Opciones para los equipos (Team 1 y Team 2)
  const teamOptions = [
    "Arturo Coello Manso/Agustín Tapia",
    "Juan Lebrón Chincoa/Alejandro Galán Romo"
  ];

  // Fondo (gradiente + imagen)
  const containerStyle = {
    background: `
      linear-gradient(rgba(17,24,39, 0.6), rgba(17,24,39, 0.6)),
      url(${backgroundImage}) center center / cover no-repeat
    `
  };

  // Al hacer clic en PREDICT, mostramos el panel
  const handlePredict = () => {
    setShowPanel(true);
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

      {/* Quién está sirviendo */}
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

      {/* Team 1 / Team 2 */}
      <div className="row-teams">
        {/* Team 1 */}
        <div className="team-box">
          <img src={coupleImg} alt="Couple Icon" className="couple-image" />
          <div className="team-text">
            <label className="team-label">Team 1</label>
            <input
              list="team1-list"
              className="team-select"
              value={team1}
              onChange={(e) => setTeam1(e.target.value)}
              placeholder="Escribe o elige..."
            />
            <datalist id="team1-list">
              {teamOptions.map((opt) => (
                <option key={opt} value={opt} />
              ))}
            </datalist>
          </div>
        </div>

        {/* Team 2 */}
        <div className="team-box">
          <img src={coupleImg} alt="Couple Icon" className="couple-image" />
          <div className="team-text">
            <label className="team-label">Team 2</label>
            <input
              list="team2-list"
              className="team-select"
              value={team2}
              onChange={(e) => setTeam2(e.target.value)}
              placeholder="Escribe o elige..."
            />
            <datalist id="team2-list">
              {teamOptions.map((opt) => (
                <option key={opt} value={opt} />
              ))}
            </datalist>
          </div>
        </div>
      </div>

      {/* Stats Team 1 */}
      <div className="row-stats">
        <div className="icon-slot">
          {serving === "team1" && (
            <img src={ballImg} alt="Ball" className="serving-ball" />
          )}
        </div>
        <div className="stats-box">
          <label className="stats-label">POINTS</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={pointsT1}
            onChange={(e) => setPointsT1(e.target.value)}
          />
        </div>
        <div className="stats-box">
          <label className="stats-label">GAMES</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={gamesT1}
            onChange={(e) => setGamesT1(e.target.value)}
          />
        </div>
        <div className="stats-box">
          <label className="stats-label">SET</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={setsT1}
            onChange={(e) => setSetsT1(e.target.value)}
          />
        </div>
      </div>

      {/* Stats Team 2 */}
      <div className="row-stats">
        <div className="icon-slot">
          {serving === "team2" && (
            <img src={ballImg} alt="Ball" className="serving-ball" />
          )}
        </div>
        <div className="stats-box">
          <label className="stats-label">POINTS</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={pointsT2}
            onChange={(e) => setPointsT2(e.target.value)}
          />
        </div>
        <div className="stats-box">
          <label className="stats-label">GAMES</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={gamesT2}
            onChange={(e) => setGamesT2(e.target.value)}
          />
        </div>
        <div className="stats-box">
          <label className="stats-label">SET</label>
          <input
            type="number"
            className="stats-input"
            placeholder="0"
            value={setsT2}
            onChange={(e) => setSetsT2(e.target.value)}
          />
        </div>
      </div>

      {/* Botón para predecir */}
      <button className="predict-button" onClick={handlePredict}>
        PREDICT
      </button>

      {/* Overlay y Panel vistoso cuando showPanel es true */}
      {showPanel && (
        <>
          {/* Capa semitransparente que cubre toda la pantalla */}
          <div className="prediction-overlay" onClick={() => setShowPanel(false)} />

          {/* Panel centrado en pantalla */}
          <div className="prediction-panel">
            <h2>¡Predicción Generada! <span role="img" aria-label="crystal-ball">🔮</span></h2>
            <p>
              Aquí puedes mostrar la información o 
              resultado de tu predicción con tus colores corporativos y emojis. 
            </p>
            <button className="close-panel" onClick={() => setShowPanel(false)}>
              Cerrar
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Prediction;
