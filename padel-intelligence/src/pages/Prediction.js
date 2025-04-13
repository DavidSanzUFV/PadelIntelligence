import React, { useState, useEffect } from "react";
import FormattedPredictionResult from "../components/FormattedPredictionResult";
import "../styles/Prediction.css";
//import logo from "../assets/logo.png";
// Icons
import servingImg from "../assets/whoisserving.png";
//import coupleImg from "../assets/couple.png";
import ballImg from "../assets/bola.png";

const Prediction = () => {
  const [pairs, setPairs] = useState([]);
  const [team1, setTeam1] = useState("");
  const [team2, setTeam2] = useState("");
  const [search1, setSearch1] = useState("");
  const [search2, setSearch2] = useState("");
  const [serving, setServing] = useState("");
  const [setsT1, setSetsT1] = useState("0");
  const [gamesT1, setGamesT1] = useState("0");
  const [pointsT1, setPointsT1] = useState("0");
  const [setsT2, setSetsT2] = useState("0");
  const [gamesT2, setGamesT2] = useState("0");
  const [pointsT2, setPointsT2] = useState("0");
  const [showInfo, setShowInfo] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch de los nombres de las parejas
  useEffect(() => {
    const fetchPairs = async () => {
      try {
        const response = await fetch("/api/pairs_name");
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        setPairs(data.pairs);
      } catch (error) {
        console.error("Error fetching pair names:", error);
      }
    };
    fetchPairs();
  }, []);
  
  const [isTiebreak, setIsTiebreak] = useState(false);

  useEffect(() => {
    if ((gamesT1 === "6" && gamesT2 === "6") || (gamesT1 === 6 && gamesT2 === 6)) {
      setIsTiebreak(true);
    } else {
      setIsTiebreak(false);
    }
  }, [gamesT1, gamesT2]);
  
  // Estado para almacenar el resultado de la predicción
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  
  const handlePredict = async () => {
    const matchData = {
      t1_points: pointsT1,
      t2_points: pointsT2,
      t1_games: parseInt(gamesT1),
      t2_games: parseInt(gamesT2),
      t1_sets: parseInt(setsT1),
      t2_sets: parseInt(setsT2),
      serve: serving === "team1" ? 1 : 2,
      p_serve: 0.8,
      p_games_won_on_serve: 0.7,
    };
  
    try {
      setIsLoading(true); // 👈 mostrar loading
      const response = await fetch("/api/run_prediction/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(matchData),
      });
      const prediction = await response.json();
      setPredictionResult(prediction);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error during prediction:", error);
      alert("Error while fetching prediction.");
    } finally {
      setIsLoading(false); // 👈 ocultar loading
    }
  };
  
  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="prediction-container">
      <div className="prediction-main-card">
        <div className="info-wrapper">
        {showInfo && (
  <div className="info-box top">
    <p>
      Enter the current match result by specifying the teams that are playing and the points, games, and sets currently in progress.
      Click on <b>PREDICT</b> to receive key insights and potential outcomes of the match.
    </p>
  </div>
)}
          <h1 className="prediction-title">
            PREDICT A MATCH
            <span className="info-icon" onClick={() => setShowInfo(!showInfo)}>ℹ️</span>
          </h1>
        </div>
        
      <div className="pair-selection">
        {/* Buscador del Equipo 1 */}
        <div className="team-box">
          <input
            type="text"
            placeholder="Select Team 1"
            value={search1}
            onChange={(e) => setSearch1(e.target.value)}
            className="team-input"
          />
          {search1 && (
            <div className="autocomplete-list">
              {pairs
                .filter((pair) =>
                  pair.toLowerCase().includes(search1.toLowerCase())
                )
                .slice(0, 5)
                .map((pair, index) => (
                  <div
                    key={index}
                    className="autocomplete-option"
                    onClick={() => {
                      setTeam1(pair);
                      setSearch1("");
                    }}
                  >
                    {pair}
                  </div>
                ))}
            </div>
          )}
          {team1 && <div className="selected-team">{team1}</div>}
        </div>

        <div className="vs-label">VS</div>

        {/* Buscador del Equipo 2 */}
        <div className="team-box">
          <input
            type="text"
            placeholder="Select Team 2"
            value={search2}
            onChange={(e) => setSearch2(e.target.value)}
            className="team-input"
          />
          {search2 && (
            <div className="autocomplete-list">
              {pairs
                .filter((pair) =>
                  pair.toLowerCase().includes(search2.toLowerCase())
                )
                .slice(0, 5)
                .map((pair, index) => (
                  <div
                    key={index}
                    className="autocomplete-option"
                    onClick={() => {
                      setTeam2(pair);
                      setSearch2("");
                    }}
                  >
                    {pair}
                  </div>
                ))}
            </div>
          )}
          {team2 && <div className="selected-team">{team2}</div>}
        </div>
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
              <option value="team1">{team1 || "Team 1"}</option>
              <option value="team2">{team2 || "Team 2"}</option>
            </select>
          </div>
        </div>

        {/* Estadísticas del Equipo 1 */}
        <div className="row-stats">
          <div className="icon-slot">
            {serving === "team1" && <img src={ballImg} alt="Ball" className="serving-ball" />}
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

      <div className="stats-box">
        <label className="stats-label">POINTS</label>
        <select
          className="stats-input"
          value={pointsT1}
          onChange={(e) => setPointsT1(e.target.value)}
        >
          {isTiebreak ? (
            [...Array(14).keys()].map((point) => (
              <option key={point} value={point}>{point}</option>
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

        {/* Estadísticas del Equipo 2 */}
        <div className="row-stats">
          <div className="icon-slot">
            {serving === "team2" && <img src={ballImg} alt="Ball" className="serving-ball" />}
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

                  <div className="stats-box">
          <label className="stats-label">POINTS</label>
          <select
            className="stats-input"
            value={pointsT2}
            onChange={(e) => setPointsT2(e.target.value)}
          >
            {isTiebreak ? (
              [...Array(14).keys()].map((point) => (
                <option key={point} value={point}>{point}</option>
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
      {/* Botón de Predicción centrado debajo de las estadísticas */}
      <div className="button-container">
        {team1 && team2 && (
          <button className="predict-button" onClick={handlePredict}>
            PREDICT
          </button>
        )}
      </div>
      {isLoading && (
  <div className="modal-overlay-pre">
    <div className="modal-contenido">
      <span className="loading-spinner">⏳</span>
      <h2>Generating prediction...</h2>
    </div>
  </div>
)}

      {/* Modal para mostrar el resultado de la predicción */}
      {predictionResult && isModalOpen && (
        <div className="modal-overlay-pre" onClick={closeModal}>
          <div className="modal-contenido" onClick={(e) => e.stopPropagation()}>
            <span className="close-button" onClick={closeModal}>&times;</span>
            <h2>
  Victory prediction for
  <br />
  <span style={{ fontStyle: "italic", color: "#d0d0ff" }}>
    {team1}
  </span>{" "}
  <span style={{ fontWeight: "normal", fontStyle: "italic", color: "#aaa" }}>
    vs {team2}
  </span>
</h2>


            <div className="prediction-result">
              <FormattedPredictionResult predictionResult={predictionResult} />
            </div>
          </div>
        </div>
      )}

    </div>
    </div>
  );
};

export default Prediction;
