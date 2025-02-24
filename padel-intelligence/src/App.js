import React from "react";
import { Routes, Route } from "react-router-dom"; // No importar BrowserRouter
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Couples from "./pages/Couples";
import Prediction from "./pages/Prediction";
import Statistics from "./pages/Statistics";
import "./styles/App.css";

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <div className="content-container">
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/couples" element={<Couples />} />
            <Route path="/prediction" element={<Prediction />} />
            <Route path="/statistics" element={<Statistics />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
