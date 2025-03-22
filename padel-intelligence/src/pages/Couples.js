import React, { useEffect, useState } from "react";
import "../styles/Couples.css";
import statsIcon from "../assets/stats-icon.png"; // Asegúrate de tener esta imagen

// Importa el fondo
import backgroundImage from "../assets/fondohome.jpg";

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

const Couples = () => {
  const [pairs, setPairs] = useState([]);
  const [genderFilter, setGenderFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/pairs")
      .then((response) => response.json())
      .then((data) => {
        const filteredData = data.filter(pair => pair.gender === "M" || pair.gender === "W");
        setPairs(filteredData);
      })
      .catch((error) => console.error("Error fetching pairs:", error));
  }, []);

  // Filtrar por género y búsqueda
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
    <div className="couples-container" style={{ background: `url(${backgroundImage}) center center / cover no-repeat` }}>
      <h2 className="couples-title">Player Couples</h2>
      <p className="couples-description">
        View and analyze player couples, their performance, and statistics.
      </p>

      {/* Filtros */}
      <div className="controls-container">
        <div className="filter-container">
          <label htmlFor="genderFilter">Filter by gender:</label>
          <select
            id="genderFilter"
            value={genderFilter}
            onChange={(e) => setGenderFilter(e.target.value)}
          >
            <option value="all">All</option>
            <option value="M">Man</option>
            <option value="W">woman</option>
          </select>
        </div>

        {/* Buscador */}
        <div className="search-container">
          <input
            type="text"
            placeholder="Search player..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Lista de parejas con imágenes */}
      <div className="couples-grid">
        {filteredPairs.length > 0 ? (
          filteredPairs.map((pair, index) => (
            <div key={index} className="couple-card">
              <div className="player-info">
                <img src={pair.photo1} alt={pair.player1} className="player-photo" />
                <img src={getFlagURL(pair.nationality1)} alt="Flag" className="flag-img" />
                <span className="player-name">{formatName(pair.player1)}</span>
              </div>
              <div className="player-info">
              <span className="player-name">{formatName(pair.player2)}</span>
                <img src={pair.photo2} alt={pair.player2} className="player-photo" />
                <img src={getFlagURL(pair.nationality2)} alt="Flag" className="flag-img" />
              </div>
              <div className="stats-icon">
                <img src={statsIcon} alt="Stats" />
              </div>
            </div>
          ))
        ) : (
          <p>No couples found.</p>
        )}
      </div>
    </div>
  );
};

export default Couples;
