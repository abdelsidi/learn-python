import React from "react";
import { useNavigate } from "react-router-dom";

const styles = {
  container: {
    maxWidth: "800px",
    margin: "6rem auto",
    textAlign: "center",
    padding: "0 2rem",
  },
  title: { fontSize: "3rem", fontWeight: "800", color: "#f1f5f9", marginBottom: "1rem" },
  subtitle: { fontSize: "1.2rem", color: "#94a3b8", marginBottom: "2.5rem", lineHeight: "1.8" },
  buttons: { display: "flex", gap: "1rem", justifyContent: "center" },
  primary: {
    background: "#3b82f6",
    color: "#fff",
    border: "none",
    padding: "0.75rem 2rem",
    borderRadius: "8px",
    fontSize: "1rem",
    fontWeight: "600",
  },
  secondary: {
    background: "transparent",
    color: "#60a5fa",
    border: "2px solid #3b82f6",
    padding: "0.75rem 2rem",
    borderRadius: "8px",
    fontSize: "1rem",
    fontWeight: "600",
  },
  features: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "1.5rem",
    marginTop: "4rem",
  },
  card: {
    background: "#1e293b",
    padding: "1.5rem",
    borderRadius: "12px",
    border: "1px solid #334155",
  },
  cardTitle: { fontWeight: "700", marginBottom: "0.5rem", color: "#f1f5f9" },
  cardText: { color: "#94a3b8", fontSize: "0.9rem", lineHeight: "1.6" },
};

const features = [
  { title: "Interactive Exercises", text: "Write and run real Python code directly in your browser." },
  { title: "Instant Feedback", text: "See results immediately with auto-grading and helpful hints." },
  { title: "Track Progress", text: "Follow a structured curriculum from basics to OOP." },
];

export default function Home() {
  const navigate = useNavigate();
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Learn Python by Doing</h1>
      <p style={styles.subtitle}>
        Master Python through hands-on coding exercises.<br />
        6 lessons covering Basics, Control Flow, Functions, Data Structures, OOP, and Error Handling.
      </p>
      <div style={styles.buttons}>
        <button style={styles.primary} onClick={() => navigate("/register")}>Get Started Free</button>
        <button style={styles.secondary} onClick={() => navigate("/login")}>Login</button>
      </div>
      <div style={styles.features}>
        {features.map((f) => (
          <div key={f.title} style={styles.card}>
            <div style={styles.cardTitle}>{f.title}</div>
            <div style={styles.cardText}>{f.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
