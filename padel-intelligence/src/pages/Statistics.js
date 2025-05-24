import React, { useEffect, useState } from "react";
import "../styles/Statistics.css";
import LobsPieChart from "../components/LobsPieChart"; 
import RadarStatsChart from "../components/RadarStatsChart"; 
import statsIcon from "../assets/stats-icon.png"; 

const getFlagURL = (nationality) => {
  if (!nationality) return "/flags/default.png";

  const countryCodes = {
    Argentina: "ar", Belgium: "be", Brazil: "br", Chile: "cl", Egypt: "eg",
    Finland: "fi", France: "fr", Italy: "it", Kuwait: "kw", Mexico: "mx",
    Netherlands: "nl", Paraguay: "py", Portugal: "pt", Qatar: "qa", Russia: "ru",
    Saudi_Arabia: "sa", Spain: "es", Sweden: "se", USA: "us", Venezuela: "ve"
  };
  return `https://flagcdn.com/w80/${countryCodes[nationality]?.toLowerCase()}.png`;
};


const getBrandLogo = (brand) => {
  if (!brand) return "/assets/brands/default.png";

  const formattedBrand = brand
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "")
    .replace(/[^a-zA-Z0-9]/g, "")
    .toLowerCase();

  return `/assets/brands/${formattedBrand}.png`;
};
const Modal = ({ player, onClose, tabs, activeTab, setActiveTab, benchmarkMax, benchmark }) => {
  const [playerStats, setPlayerStats] = useState(null);

  useEffect(() => {
    if (player) {
      fetch(`/api/player_stats/${encodeURIComponent(player.player)}`)
        .then(res => res.json())
        .then(data => setPlayerStats(data))
        .catch(err => console.error("❌ Error fetching stats:", err));
    }
  }, [player]);

  if (!player) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        <h2>{player.player}'s Stats</h2>

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
          {playerStats ? (
            <>
              {activeTab === "tournaments" && (
                <>
                  <p>🏆 Tournaments Played: {playerStats.tournaments_played}</p>
                  <p>🎾 Matches Played: {playerStats.matches_played}</p>
                  <p>📈 Win Rate: {playerStats.win_rate}%</p>
                </>
              )}
              {activeTab === "serves" && (
                <>
                  <p>🎯 % First Serves: {playerStats.percentage_1st_serves}%</p>
                  <p>🧱 % Service Games Won: {playerStats.percentage_service_games_won}%</p>
                </>
              )}
              {activeTab === "tactics" && (
                <>
                  <p>🧠 % Cross-court Shots: {playerStats.percentage_cross}%</p>
                  <p>🛣️ % Parallel Shots: {playerStats.percentage_parallel}%</p>
                </>
              )}
              {activeTab === "returns" && (
                <>
                  <p>☁️ % Lob Returns: {playerStats.percentage_lobbed_returns}%</p>
                  <p>➖ % Flat Returns: {playerStats.percentage_flat_returns}%</p>
                  <p>⚠️ % Return Errors: {playerStats.percentage_return_errors}%</p>
                </>
              )}
              {activeTab === "aerial game" && (
                <>
                  <p>🌪️ Lobs Received per Match: {playerStats.lobs_received_per_match}</p>
                  <p>💥 % Smashes from Lobs: {playerStats.percentage_smashes_from_lobs}%</p>
                  <p>🌀 % Rulos from Lobs: {playerStats.percentage_rulos_from_lobs}%</p>
                  <p>🔃 % Viborejas from Lobs: {playerStats.percentage_viborejas_from_lobs}%</p>
                  <p>🔽 % Bajadas from Lobs: {playerStats.percentage_bajadas_from_lobs}%</p>
                  <p>🏅 % Winners from Lobs: {playerStats.winners_from_lobs}%</p>
                </>
              )}
              {activeTab === "defense" && (
                <>
                  <p>🛡️ Outside Recoveries: {playerStats.outside_recoveries}</p>
                  <p>🎈 Lobs Played per Match: {playerStats.lobs_played_per_match}</p>
                  <p>🕸️ % Net Recovery with Lob: {playerStats.net_recovery_with_lob}%</p>
                  <p>❌ Unforced Errors per Match: {playerStats.unforced_errors_per_match}</p>
                </>
              )}
              {activeTab === "graphs" && (
                <div className="charts-row">
                  <div className="chart-container">
                    <LobsPieChart stats={playerStats} />
                  </div>
                  <div className="chart-container">
                    <RadarStatsChart
                      stats={playerStats}
                      benchmarkMax={benchmarkMax}
                      benchmark={benchmark}
                      gender={player.gender}
                      label="Player"
                    />
                  </div>
                </div>
              )}
            </>
          ) : (
            <p style={{ marginTop: "20px" }}>Loading stats...</p>
          )}
        </div>
      </div>
    </div>
  );
};


const allowedNationalities = ["Spain", "Argentina", "France"];

const tabs = [
  { key: "tournaments", label: "🎾 Tournaments" },
  { key: "serves", label: "🎯 Serves" },
  { key: "tactics", label: "🧠 Tactics" },
  { key: "returns", label: "↩️ Returns" },
  { key: "aerial game", label: "🚀 Aerial game" },
  { key: "defense", label: "🛡️ Defense" },
  { key: "graphs", label: "📊 Graphs" }
];

const fetchBenchmark = async () => {
  try {
    const response = await fetch("/api/benchmark");
    if (!response.ok) throw new Error("Error fetching benchmark");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("❌ Error fetching benchmark:", error);
    return null;
  }
};

const fetchBenchmarkMax = async () => {
  try {
    const response = await fetch("/api/benchmark_max");
    if (!response.ok) throw new Error("Error fetching benchmark max");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("❌ Error fetching benchmark max:", error);
    return null;
  }
};

const Statistics = () => {
  const [activeTab, setActiveTab] = useState("tournaments");
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [modalPlayer, setModalPlayer] = useState(null);
  const [benchmarkMax, setBenchmarkMax] = useState(null); 
  const [benchmark, setBenchmark] = useState(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [genderFilter, setGenderFilter] = useState("All");
  const [nationalityFilter, setNationalityFilter] = useState("All");
  const [handFilter, setHandFilter] = useState("All");
  const [sideFilter, setSideFilter] = useState("All");
  const [brandFilter, setBrandFilter] = useState("All");
  const [sortOrder, setSortOrder] = useState("name_asc");

  useEffect(() => {
    fetch("/api/players")
      .then((response) => response.json())
      .then((data) => {
        console.log("📢 Data recibida del backend:", data);

        const uniquePlayers = {};
        data.forEach((player) => {
          const key = player.player;
          if (!uniquePlayers[key]) {
            uniquePlayers[key] = { ...player, side: new Set([player.side]) };
          } else {
            uniquePlayers[key].side.add(player.side);
          }
        });

        // Convertir 'side' en texto legible (Right side, Left side o Both sides)
        const formattedPlayers = Object.values(uniquePlayers).map((player) => ({
          ...player,
          side: player.side.size > 1 ? "Both sides" : player.side.has("Right") ? "Right side" : "Left side"
        }));

        setPlayers(formattedPlayers);
        setFilteredPlayers(formattedPlayers);
      })
      .catch((error) => console.error("🚨 Error fetching players:", error));

      const fetchBenchmarks = async () => {
        try {
          const maxData = await fetchBenchmarkMax();
          const avgData = await fetchBenchmark();
    
          if (maxData) {
            console.log("✅ Benchmark máximo obtenido:", maxData);
            setBenchmarkMax(maxData);
          } else {
            console.error("❌ Error al obtener el benchmark máximo");
          }
    
          if (avgData) {
            console.log("✅ Benchmark obtenido:", avgData);
            setBenchmark(avgData);
          } else {
            console.error("❌ Error al obtener el benchmark");
          }
        } catch (error) {
          console.error("❌ Error en fetch de benchmarks:", error);
        }
      };
      fetchBenchmarks();
  }, []);

  useEffect(() => {
    let filtered = players.filter(player =>
      (searchQuery === "" || player.player.toLowerCase().includes(searchQuery.toLowerCase())) &&
      (genderFilter === "All" || player.gender?.toUpperCase() === genderFilter.toUpperCase()) &&
      (nationalityFilter === "All" ||
        (nationalityFilter === "Others" ? !allowedNationalities.includes(player.nationality) : player.nationality === nationalityFilter)) &&
      (handFilter === "All" || player.hand === handFilter) &&
      (sideFilter === "All" ||
        (sideFilter === "Right" && player.side === "Right side") ||
        (sideFilter === "Left" && player.side === "Left side") ||
        (sideFilter === "Both" && player.side === "Both sides")) &&
      (brandFilter === "All" || (brandFilter === "Others" ? !["Bullpadel", "Nox", "Adidas", "Joma", "Siux"].includes(player.brand) : player.brand === brandFilter))
    );

    

    // Ordenar jugadores
    if (sortOrder === "name_asc") {
      filtered.sort((a, b) => a.player.localeCompare(b.player));
    } else if (sortOrder === "name_desc") {
      filtered.sort((a, b) => b.player.localeCompare(a.player));
    }

    setFilteredPlayers(filtered);
  }, [searchQuery, genderFilter, nationalityFilter, handFilter, sideFilter, brandFilter, sortOrder, players]);

  const clearFilters = () => {
    setSearchQuery("");
    setGenderFilter("All");
    setNationalityFilter("All");
    setHandFilter("All");
    setSideFilter("All");
    setBrandFilter("All");
    setSortOrder("name_asc");
  };
  useEffect(() => {
    document.body.style.overflow = modalPlayer ? 'hidden' : 'auto';
  }, [modalPlayer]);
  
  return (
    <div className="statistics-container">
      <h1 className="title">INDIVIDUAL STATISTICS</h1>
      <p className="subtitle">Click on a player to see detailed statistics.</p>

      {/* Filters menus */}
      <div className="filters-container">
        <input type="text" placeholder="Search player..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
        
        <select value={genderFilter} onChange={(e) => setGenderFilter(e.target.value)}>
          <option value="All">All Genders</option>
          <option value="M">Men</option>
          <option value="W">Women</option>
        </select>

        <select value={nationalityFilter} onChange={(e) => setNationalityFilter(e.target.value)}>
          <option value="All">All Nationalities</option>
          <option value="Spain">Spain</option>
          <option value="Argentina">Argentina</option>
          <option value="France">France</option>
          <option value="Others">Others</option>
        </select>

        <select value={handFilter} onChange={(e) => setHandFilter(e.target.value)}>
          <option value="All">All Hands</option>
          <option value="Right">Right-handed</option>
          <option value="Left">Left-handed</option>
        </select>

        <select value={sideFilter} onChange={(e) => setSideFilter(e.target.value)}>
          <option value="All">All Sides</option>
          <option value="Right">Right side</option>
          <option value="Left">Left side</option>
          <option value="Both">Both sides</option>
        </select>

        <select value={brandFilter} onChange={(e) => setBrandFilter(e.target.value)}>
          <option value="All">All Brands</option>
          <option value="Bullpadel">Bullpadel</option>
          <option value="Nox">Nox</option>
          <option value="Adidas">Adidas</option>
          <option value="Joma">Joma</option>
          <option value="Siux">Siux</option>
          <option value="Others">Others</option>
        </select>

        <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
          <option value="name_asc">Name A-Z</option>
          <option value="name_desc">Name Z-A</option>
        </select>

        {/* Clear filters */}
        <button className="clear-filters-button" onClick={clearFilters}>Clear Filters</button>
      </div>

      {/* Players list */}
      <div className="players-grid">
        {filteredPlayers.length > 0 ? (
          filteredPlayers.map((player, index) => (
            <div key={index} className="player-card">
              <div className="player-name">{player.player}</div>
              <div className="player-photo-container">
                <img src={getFlagURL(player.nationality)} alt="Flag" className="player-flag" />
                <img src={player.photo} alt="player_photo" className="player-photo" />
                <img src={getBrandLogo(player.brand)} alt={player.brand} className="brand-logo" />
              </div>
              <div className="player-details">
                <span className="hand-text">{player.hand === "Right" ? "Right-handed" : "Left-handed"}</span>
                <span className="side-text">{player.side}</span>
              </div>
              <div className="stats-icon" onClick={() => setModalPlayer(player)}>
              <img src={statsIcon} alt="Stats" />
            </div>
            </div>
          ))
        ) : (
          <p>No players found.</p>
        )}
      </div>
      {modalPlayer && (
        <Modal
          player={modalPlayer}
          onClose={() => setModalPlayer(null)}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          benchmarkMax={benchmarkMax}
          benchmark={benchmark}
          tabs={tabs}
        />
)}
    </div>
  );
};

export default Statistics;
