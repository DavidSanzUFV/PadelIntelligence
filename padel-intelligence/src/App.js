import React from "react";
import { Routes, Route } from "react-router-dom"; 
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Couples from "./pages/Couples";
import Prediction from "./pages/Prediction";
import Statistics from "./pages/Statistics";
import Highlights from "./pages/Highlights"; 
import Curiosities from "./pages/Curiosities";
import Comparator from "./pages/Comparator";
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
            <Route path="/highlights" element={<Highlights />} />
            <Route path="/curiosities" element={<Curiosities />} />
            <Route path="/comparator" element={<Comparator />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
