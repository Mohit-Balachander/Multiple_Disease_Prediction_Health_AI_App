import React from "react";
import { Link } from "react-scroll";

// Simple inline SVG for the logo
const Logo = () => (
  <svg
    width="40"
    height="40"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 2L12 22" />
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </svg>
);

function Sidebar({ theme, toggleTheme }) {
  const navLinks = [
    { to: "diabetes", label: "Diabetes" },
    { to: "heart", label: "Heart Disease" },
    { to: "parkinsons", label: "Parkinsons" },
    { to: "stroke", label: "Stroke" },
    { to: "comparison", label: "Model Comparison" },
  ];

  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <div className="logo-container">
          <Logo />
          <h2>Health AI</h2>
        </div>
        <div className="theme-toggle-container">
          <span>☀️</span>
          <label className="switch">
            <input
              type="checkbox"
              onChange={toggleTheme}
              checked={theme === "dark"}
            />
            <span className="slider round"></span>
          </label>
          <span>🌙</span>
        </div>
      </div>
      <ul>
        {navLinks.map((link) => (
          <li key={link.to}>
            <Link
              to={link.to}
              spy={true}
              smooth={true}
              offset={-70}
              duration={500}
              activeClass="active"
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
// Add this CSS directly into the Sidebar.js for simplicity
const styles = `
.sidebar {
  width: 280px; position: fixed; top: 0; left: 0; height: 100vh;
  background-color: var(--sidebar-bg); backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); border-right: 1px solid var(--border-color);
  padding: 25px; display: flex; flex-direction: column; z-index: 10;
  transition: background-color 0.3s, border-color 0.3s;
}
.sidebar-header { text-align: center; margin-bottom: 30px; }
.logo-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 20px;}
.sidebar-header h2 { color: var(--primary-color); margin: 0; font-weight: 600; }
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar li {
  padding: 15px 20px; margin-bottom: 10px; border-radius: 8px; cursor: pointer;
  transition: background-color 0.2s, color 0.2s, transform 0.2s; font-weight: 500;
}
.sidebar li a { display: block; color: var(--text-color); }
.sidebar li:hover { background-color: var(--primary-hover); }
.sidebar li:hover a { color: white; }
.sidebar li a.active { color: var(--primary-color); font-weight: 600; }
.theme-toggle-container {
  display: flex; justify-content: center; align-items: center; gap: 10px;
}
.switch { position: relative; display: inline-block; width: 50px; height: 28px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; }
input:checked + .slider { background-color: var(--primary-color); }
input:checked + .slider:before { transform: translateX(22px); }
.slider.round { border-radius: 34px; }
.slider.round:before { border-radius: 50%; }
.content-container { margin-left: 280px; } /* Offset content for fixed sidebar */
`;

const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

export default Sidebar;
