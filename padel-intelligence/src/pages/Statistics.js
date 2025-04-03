import React, { useEffect, useState } from "react";
import "../styles/Statistics.css";
import LobsPieChart from "../components/LobsPieChart"; // Ajusta la ruta si es necesario
import RadarStatsChart from "../components/RadarStatsChart"; // ajusta la ruta si hace falta
import statsIcon from "../assets/stats-icon.png"; // Asegúrate de tener esta imagen

// Función para obtener la bandera
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


// Función para obtener la imagen de la marca
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
const Modal = ({ player, onClose, tabs, activeTab, setActiveTab }) => {
  const [playerStats, setPlayerStats] = useState(null);

  useEffect(() => {
    if (player) {
      fetch(`/player_stats/${encodeURIComponent(player.player)}`)
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

        {playerStats ? (
          <div className="tab-content">
            {activeTab === "tournaments" && (
              <ul>
                <li><strong>Tournaments Played:</strong> {playerStats.tournaments_played}</li>
                <li><strong>Matches Played:</strong> {playerStats.matches_played}</li>
                <li><strong>Win Rate:</strong> {playerStats.win_rate}%</li>
              </ul>
            )}
            {activeTab === "serves" && (
              <ul>
                <li><strong>% First Serves:</strong> {playerStats.percentage_1st_serves}%</li>
                <li><strong>% Service Games Won:</strong> {playerStats.percentage_service_games_won}%</li>
              </ul>
            )}
            {activeTab === "tactics" && (
              <ul>
                <li><strong>% Cross-court Shots:</strong> {playerStats.percentage_cross}%</li>
                <li><strong>% Parallel Shots:</strong> {playerStats.percentage_parallel}%</li>
              </ul>
            )}
            {activeTab === "returns" && (
              <ul>
                <li><strong>% Lob Returns:</strong> {playerStats.percentage_lobbed_returns}%</li>
                <li><strong>% Flat Returns:</strong> {playerStats.percentage_flat_returns}%</li>
                <li><strong>% Error Returns:</strong> {playerStats.percentage_return_errors}%</li>
              </ul>
            )}
            {activeTab === "aerial game" && (
              <ul>
                <li><strong>Lobs Received per Match:</strong> {playerStats.lobs_received_per_match}</li>
                <li><strong>% Smashes from Lobs:</strong> {playerStats.percentage_smashes_from_lobs}%</li>
                <li><strong>% Rulos from Lobs:</strong> {playerStats.percentage_rulos_from_lobs}%</li>
                <li><strong>% Viborejas from Lobs:</strong> {playerStats.percentage_viborejas_from_lobs}%</li>
                <li><strong>% Bajadas from Lobs:</strong> {playerStats.percentage_bajadas_from_lobs}%</li>
                <li><strong>% Winners from Lobs:</strong> {playerStats.winners_from_lobs}%</li>
              </ul>
            )}
            {activeTab === "defense" && (
              <ul>
                <li><strong>Outside Recoveries:</strong> {playerStats.outside_recoveries}</li>
                <li><strong>Lobs Played per Match:</strong> {playerStats.lobs_played_per_match}</li>
                <li><strong>% Net Recovery with Lob:</strong> {playerStats.net_recovery_with_lob}%</li>
                <li><strong>Unforced Errors per Match:</strong> {playerStats.unforced_errors_per_match}</li>
              </ul>
            )}
            {activeTab === "graphs" && (
              <>
                <div className="charts-row">
                  <div className="chart-container">
                    <LobsPieChart stats={playerStats} />
                  </div>
                  <div className="chart-container">
                    <RadarStatsChart stats={playerStats} />
                  </div>
                </div>
              </>
            )}
          </div>
        ) : (
          <p style={{ marginTop: "20px" }}>Loading stats...</p>
        )}
      </div>
    </div>
  );
};

const allowedNationalities = ["Spain", "Argentina", "France"];

const tabs = [
  { key: "tournaments", label: "🎾 tournaments" },
  { key: "serves", label: "🎯 serves" },
  { key: "tactics", label: "🧠 tactics" },
  { key: "returns", label: "↩️ returns" },
  { key: "aerial game", label: "🚀 aerial game" },
  { key: "defense", label: "🛡️ defense" },
  { key: "graphs", label: "📊 graphs" }
];

const Statistics = () => {
  const [activeTab, setActiveTab] = useState("tournaments");
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [modalPlayer, setModalPlayer] = useState(null);

  // Estados para filtros
  const [searchQuery, setSearchQuery] = useState("");
  const [genderFilter, setGenderFilter] = useState("All");
  const [nationalityFilter, setNationalityFilter] = useState("All");
  const [handFilter, setHandFilter] = useState("All");
  const [sideFilter, setSideFilter] = useState("All");
  const [brandFilter, setBrandFilter] = useState("All");
  const [sortOrder, setSortOrder] = useState("name_asc");

  useEffect(() => {
    fetch("/players")
      .then((response) => response.json())
      .then((data) => {
        console.log("📢 Data recibida del backend:", data);

        // 🔹 Agrupar jugadores únicos y combinar valores de 'side'
        const uniquePlayers = {};
        data.forEach((player) => {
          const key = player.player;
          if (!uniquePlayers[key]) {
            uniquePlayers[key] = { ...player, side: new Set([player.side]) };
          } else {
            uniquePlayers[key].side.add(player.side);
          }
        });

        // 🔹 Convertir `side` en texto legible (Right side, Left side o Both sides)
        const formattedPlayers = Object.values(uniquePlayers).map((player) => ({
          ...player,
          side: player.side.size > 1 ? "Both sides" : player.side.has("Right") ? "Right side" : "Left side"
        }));

        setPlayers(formattedPlayers);
        setFilteredPlayers(formattedPlayers);
      })
      .catch((error) => console.error("🚨 Error fetching players:", error));
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

  // 🔹 Función para limpiar los filtros
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

      {/* 📌 Menú de Filtros */}
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

        {/* 📌 Botón para limpiar filtros */}
        <button className="clear-filters-button" onClick={clearFilters}>Clear Filters</button>
      </div>

      {/* 📌 Lista de Jugadores */}
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
      <Modal
        player={modalPlayer}
        onClose={() => setModalPlayer(null)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        tabs={tabs}
      />
    </div>
  );
};

export default Statistics;
