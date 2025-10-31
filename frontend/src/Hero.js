import React from "react";
import { Link } from "react-scroll";
import heroImage from "./assets/Image3.png";

function Hero() {
  const heroStyle = {
    backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url(${heroImage})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    color: "var(--hero-text)",
    textAlign: "center",
  };

  return (
    <section id="hero" className="section" style={heroStyle}>
      <div className="hero-content">
        <h1>Predictive Health, Powered by AI</h1>
        <p className="hero-subtitle">
          Get instant, data-driven risk assessments for Diabetes, Heart Disease,
          Parkinson's, and Stroke using our advanced prediction models.
        </p>
        <Link
          to="diabetes"
          smooth={true}
          offset={-80}
          duration={500}
          className="hero-cta-button"
        >
          Start Risk Assessment
        </Link>
      </div>
    </section>
  );
}

export default Hero;
