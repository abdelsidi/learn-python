import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

const styles = {
  nav: {
    background: "#1e293b",
    padding: "0 2rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: "60px",
    borderBottom: "1px solid #334155",
  },
  logo: { fontWeight: "700", fontSize: "1.25rem", color: "#60a5fa" },
  right: { display: "flex", gap: "1rem", alignItems: "center" },
  btn: {
    background: "#3b82f6",
    color: "#fff",
    border: "none",
    padding: "0.4rem 1rem",
    borderRadius: "6px",
    fontWeight: "600",
  },
  username: { color: "#94a3b8", fontSize: "0.9rem" },
};

export default function Navbar() {
  const { user, logout } = useAuth();
  const { language, toggleLanguage } = useLanguage();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav style={styles.nav}>
      <Link to={user ? "/dashboard" : "/"} style={styles.logo}>
        Learn Python
      </Link>
      <div style={styles.right}>
        {user ? (
          <>
            <span style={styles.username}>Hi, {user.username}</span>
            <Link to="/dashboard" style={{ color: "#94a3b8", textDecoration: "none" }}>Dashboard</Link>
            <Link to="/learn" style={{ color: "#94a3b8", textDecoration: "none" }}>Learn</Link>
            <Link to="/courses" style={{ color: "#94a3b8", textDecoration: "none" }}>Courses</Link>
            <Link to="/projects" style={{ color: "#94a3b8", textDecoration: "none" }}>Projects</Link>
            <button
              style={{ ...styles.btn, background: "#1e293b", border: "1px solid #334155" }}
              onClick={toggleLanguage}
              title="Toggle language"
            >
              {language === "en" ? "عربي" : "English"}
            </button>
            <button style={styles.btn} onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: "#94a3b8", textDecoration: "none" }}>Login</Link>
            <button style={styles.btn} onClick={() => navigate("/register")}>Sign Up</button>
          </>
        )}
      </div>
    </nav>
  );
}
