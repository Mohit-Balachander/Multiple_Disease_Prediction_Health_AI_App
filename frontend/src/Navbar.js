import React from "react";
import { Link } from "react-scroll";
import { FiSun, FiMoon } from "react-icons/fi";

const Logo = () => (
  <svg
    width="32"
    height="32"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
    <path d="M22 4L12 12 9 9 4 14"></path>
  </svg>
);

function Navbar({ theme, toggleTheme }) {
  const navLinks = [
    { to: "diabetes", label: "Diabetes" },
    { to: "heart", label: "Heart Disease" },
    { to: "parkinsons", label: "Parkinsons" },
    { to: "stroke", label: "Stroke" },
    // This is the new link you added:
    { to: "comprehensive", label: "Comprehensive" },
    { to: "comparison", label: "Model Comparison" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="hero" smooth={true} duration={500} className="navbar-logo">
          <Logo />
          Health AI
        </Link>
        <ul className="nav-menu">
          {navLinks.map((link) => (
            <li className="nav-item" key={link.to}>
              <Link
                to={link.to}
                spy={true}
                smooth={true}
                offset={-80}
                duration={500}
                activeClass="active"
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        <button
          className="theme-toggle-button"
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {theme === "light" ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
