import React, { useState, useEffect } from "react";
import "./App.css";

import Navbar from "./Navbar";
import Hero from "./Hero";
import Diabetes from "./Diabetes";
import Heart from "./Heart";
import Parkinsons from "./Parkinsons";
import Stroke from "./Stroke";
import ModelComparison from "./ModelComparison";
import ComprehensiveAssessment from "./ComprehensiveAssessment"; // <-- 1. IMPORT ADDED
import Footer from "./Footer";

function App() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  return (
    <div className="App">
      <Navbar theme={theme} toggleTheme={toggleTheme} />
      <main className="main-content">
        <Hero />
        <Diabetes />
        <Heart />
        <Parkinsons />
        <Stroke />
        <ComprehensiveAssessment /> {/* <-- 2. COMPONENT ADDED */}
        <ModelComparison />
        <Footer />
      </main>
    </div>
  );
}

export default App;
