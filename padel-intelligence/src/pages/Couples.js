import React, { useEffect, useState } from "react";
import "../styles/Couples.css";
import statsIcon from "../assets/stats-icon.png"; // Asegúrate de tener esta imagen
import LobsPieChart from "../components/LobsPieChart";
import RadarStatsChart from "../components/RadarStatsChart";


const getFlagURL = (nationality) => {
  const countryCodes = {
    Argentina: "ar",
    Belgium: "be",
    Brazil: "br",
    Chile: "cl",
    Egypt: "eg",
    Finland: "fi",
    France: "fr",
    Italy: "it",
    Kuwait: "kw",
    Mexico: "mx",
    Netherlands: "nl",
    Paraguay: "py",
    Portugal: "pt",
    Qatar: "qa",
    Russia: "ru",
    Saudi_Arabia: "sa",
    Spain: "es",
    Sweden: "se",
    USA: "us",
    Venezuela: "ve"
  };
  return `https://flagcdn.com/w40/${countryCodes[nationality]?.toLowerCase()}.png`;
};
const ModalCouple = ({ couple, stats, onClose, tabs, activeTab, setActiveTab, benchmark, benchmarkMax }) => {
  if (!couple) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        <h2>Stats for {couple.player1} & {couple.player2}</h2>

        <div className="modal-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={`tab-modal ${activeTab === tab.key ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {stats ? (
            <>
              {activeTab === "tournaments" && (
                <>
                  <p>🏆 Tournaments Played: {stats.tournaments_played}</p>
                  <p>🎾 Matches Played: {stats.matches_played}</p>
                  <p>📈 Win Rate: {stats.win_rate}%</p>
                </>
              )}

              {activeTab === "serves" && (
                <>
                  <p>🎯 % First Serves: {stats.percentage_1st_serves}%</p>
                  <p>🧱 % Service Games Won: {stats.percentage_service_games_won}%</p>
                </>
              )}

              {activeTab === "tactics" && (
                <>
                  <p>🧠 % Cross-court Shots: {stats.percentage_cross}%</p>
                  <p>🛣️ % Parallel Shots: {stats.percentage_parallel}%</p>
                </>
              )}

              {activeTab === "returns" && (
                <>
                  <p>☁️ % Lob Returns: {stats.percentage_lobbed_returns}%</p>
                  <p>➖ % Flat Returns: {stats.percentage_flat_returns}%</p>
                  <p>⚠️ % Return Errors: {stats.percentage_return_errors}%</p>
                </>
              )}

              {activeTab === "aerial game" && (
                <>
                  <p>🌪️ Lobs Received per Match: {stats.lobs_received_per_match}</p>
                  <p>💥 % Smashes from Lobs: {stats.percentage_smashes_from_lobs}%</p>
                  <p>🌀 % Rulos from Lobs: {stats.percentage_rulos_from_lobs}%</p>
                  <p>🔃 % Viborejas from Lobs: {stats.percentage_viborejas_from_lobs}%</p>
                  <p>🔽 % Bajadas from Lobs: {stats.percentage_bajadas_from_lobs}%</p>
                  <p>🏅 % Winners from Lobs: {stats.winners_from_lobs}%</p>
                </>
              )}

              {activeTab === "defense" && (
                <>
                  <p>🛡️ Outside Recoveries: {stats.outside_recoveries}</p>
                  <p>🎈 Lobs Played per Match: {stats.lobs_played_per_match}</p>
                  <p>🕸️ % Net Recovery with Lob: {stats.net_recovery_with_lob}%</p>
                  <p>❌ Unforced Errors per Match: {stats.unforced_errors_per_match}</p>
                </>
              )}

                {activeTab === "graphs" && (
                  <>
                    <div className="charts-row">
                      <div className="chart-container">
                        <LobsPieChart stats={stats} />
                      </div>
                      <div className="chart-container">
                      <RadarStatsChart 
                        stats={stats}
                        benchmark={benchmark}
                        benchmarkMax={benchmarkMax}
                        gender={couple.gender}
                        label="Couple"
                      />
                      </div>
                    </div>
                  </>
                )}
            </>
          ) : (
            <p>Loading stats...</p>
          )}
        </div>
      </div>
    </div>
  );
};


const Couples = () => {
  const [pairs, setPairs] = useState([]);
  const [genderFilter, setGenderFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [modalCouple, setModalCouple] = useState(null);
  const [activeTab, setActiveTab] = useState("tournaments");
  const [coupleStats, setCoupleStats] = useState(null);
  const [benchmarkMaxCouples, setBenchmarkMaxCouples] = useState(null);
  const [benchmarkCouples, setBenchmarkCouples] = useState(null);

  const tabs = [
  { key: "tournaments", label: "🎾 tournaments" },
  { key: "serves", label: "🎯 serves" },
  { key: "tactics", label: "🧠 tactics" },
  { key: "returns", label: "↩️ returns" },
  { key: "aerial game", label: "🚀 aerial game" },
  { key: "defense", label: "🛡️ defense" },
  { key: "graphs", label: "📊 graphs" }
  ];

  useEffect(() => {
    fetch("/pairs")
      .then((response) => response.json())
      .then((data) => {
        const filteredData = data.filter(pair => pair.gender === "M" || pair.gender === "W");
        setPairs(filteredData);
      })
      .catch((error) => console.error("Error fetching pairs:", error));
  }, []);
  
  // 📊 Benchmark de parejas (promedio y máximo)
  useEffect(() => {
    const fetchBenchmarks = async () => {
      try {
        const [maxRes, avgRes] = await Promise.all([
          fetch("/benchmark_max_couples"),
          fetch("/benchmark_couples"),
        ]);
  
        const [maxData, avgData] = await Promise.all([
          maxRes.json(),
          avgRes.json(),
        ]);
  
        setBenchmarkMaxCouples(maxData);
        setBenchmarkCouples(avgData);
      } catch (err) {
        console.error("❌ Error fetching couple benchmarks:", err);
      }
    };
  
    fetchBenchmarks();
  }, []);
  
  // 🔍 Filtro por género y búsqueda
  const filteredPairs = pairs.filter((pair) => {
    const matchesGender = genderFilter === "all" || pair.gender === genderFilter;
    const matchesSearch = searchQuery === "" ||
      pair.player1.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pair.player2.toLowerCase().includes(searchQuery.toLowerCase());
  
    return matchesGender && matchesSearch;
  });
  

  const formatName = (fullName) => {
    const parts = fullName.split(" ");
    if (parts.length === 4) {
      return `${parts[0]} ${parts[1]} ${parts[2]}`; // Primer nombre + Segundo nombre + Primer apellido
    } else {
      return fullName;
    }
  };
  
  return (
    <div className="couples-container">
      <h2 className="couples-title">PLAYER COUPLES</h2>
      <p className="couples-description">
        View and analyze player couples, their performance, and statistics.
      </p>

      <div className="filters-bar">
        <select
          className="gender-select"
          value={genderFilter}
          onChange={(e) => setGenderFilter(e.target.value)}
        >
          <option value="all">All Genders</option>
          <option value="M">Men</option>
          <option value="W">Women</option>
        </select>

        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search player..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Lista de parejas con imágenes */}
      <div className="couples-grid">
        {filteredPairs.length > 0 ? (
          filteredPairs.map((pair, index) => (
          <div className="couple-row" key={index}>
            <div className="couple-card">
              <div className="player-block">
                <img src={pair.photo1} className="player-photo" alt={pair.player1} />
                <img src={getFlagURL(pair.nationality1)} className="flag-img" alt="Flag" />
                <span className="player-name">{formatName(pair.player1)}</span>
              </div>

              <div className="player-block">
                <span className="player-name">{formatName(pair.player2)}</span>
                <img src={getFlagURL(pair.nationality2)} className="flag-img" alt="Flag" />
                <img src={pair.photo2} className="player-photo" alt={pair.player2} />
              </div>
            </div>

            {/* Icono de estadísticas FUERA del card */}
            <div
                className="stats-icon-couples"
                onClick={() => {
                  setModalCouple(pair);
                  setCoupleStats(null); // limpiar antes de nuevo fetch

                  fetch(`/pair_stats/${pair.player1_id}/${pair.player2_id}`)
                    .then((res) => res.json())
                    .then((data) => {
                      setCoupleStats(data);
                    })
                    .catch((err) => {
                      console.error("❌ Error fetching couple stats:", err);
                    });
                }}
              >
                <img src={statsIcon} alt="Stats" />
            </div>

          </div>
          ))
        ) : (
          <p>No couples found.</p>
        )}
      </div>
      <ModalCouple
  couple={modalCouple}
  stats={coupleStats}
  onClose={() => {
    setModalCouple(null);
    setCoupleStats(null);
  }}
  tabs={tabs}
  activeTab={activeTab}
  setActiveTab={setActiveTab}
  benchmark={benchmarkCouples}
  benchmarkMax={benchmarkMaxCouples}
/>
    </div>
  );
};

export default Couples;
