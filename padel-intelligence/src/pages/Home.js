import React, { useState, useEffect } from "react";
import "../styles/Home.css";

// Import images
import carrousel1 from "../assets/carrousel1.webp";
import carrousel2 from "../assets/carrousel2.jpg";
import carrousel3 from "../assets/carrousel3.jpeg";
import carrousel4 from "../assets/carrousel4.jpeg";
// Import logo
import logo from "../assets/logo.png";

// Example icons from react-icons
import { FaChartLine, FaHandsHelping, FaUserTie } from "react-icons/fa";


const slides = [
  { 
    image: carrousel1, 
    caption: "Statistics and data for more accurate analysis"
  },
  { 
    image: carrousel2, 
    caption: "Discover each player's strengths and weaknesses"
  },
  { 
    image: carrousel3, 
    caption: "Get AI-based outcome predictions"
  },
  { 
    image: carrousel4, 
    caption: "All your match information in one place"
  },
];

const Home = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Automatically change image every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      handleNext();
    }, 3000);
    return () => clearInterval(interval);
  }, [currentIndex]);

  const handleNext = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === slides.length - 1 ? 0 : prevIndex + 1
    );
  };

  const handlePrev = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? slides.length - 1 : prevIndex - 1
    );
  };

  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to Padel Intelligence</h1>
      
      {/* Carousel */}
      <div className="carousel-container">
        <div
          className="carousel-slide"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {slides.map((slide, index) => (
            <div className="carousel-item" key={index}>
              <img src={slide.image} alt={`Slide ${index + 1}`} />
            </div>
          ))}
        </div>

        {/* Navigation buttons */}
        <button className="carousel-button prev" onClick={handlePrev}>
          &#10094;
        </button>
        <button className="carousel-button next" onClick={handleNext}>
          &#10095;
        </button>
      </div>

      {/* Caption below carousel */}
      <div className="carousel-caption">
        <img 
          src={logo} 
          alt="Padel Intelligence Logo" 
          className="caption-logo"
        />
        <span className="caption-text">
          {slides[currentIndex].caption}
        </span>
      </div>

      {/* Benefits Title */}
      <h3 className="benefits-title">What We Do</h3>

      {/* Benefits Section */}
      <div className="benefits-container">
        {/* Benefit 1 */}
        <div className="benefit-card">
          <FaChartLine className="benefit-icon" />
          <h4>Improve Data Analysis in Padel</h4>
          <p>
            With advanced tools, we provide detailed analysis to boost performance and strategy in every match.
          </p>
        </div>

        {/* Benefit 2 */}
        <div className="benefit-card">
          <FaHandsHelping className="benefit-icon" />
          <h4>Support the Development of Padel</h4>
          <p>
            We foster innovation and growth in the sport, contributing to the progress of players, coaches, and clubs.
          </p>
        </div>

        {/* Benefit 3 */}
        <div className="benefit-card">
          <FaUserTie className="benefit-icon" />
          <h4>Enhance and Add Value for Professionals</h4>
          <p>
            We provide relevant information that adds value to professionals and teams, elevating their competitive level.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;
