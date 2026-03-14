import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const s = {
  page: { maxWidth: "1200px", margin: "0 auto", padding: "2rem" },
  header: { marginBottom: "2rem" },
  title: { fontSize: "1.75rem", fontWeight: "700", marginBottom: "0.25rem" },
  subtitle: { color: "#94a3b8" },

  difficultyBadge: {
    beginner: { background: "#052e16", color: "#4ade80" },
    intermediate: { background: "#1e3a5f", color: "#60a5fa" },
    advanced: { background: "#4d2e3b", color: "#f472b6" },
  },

  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "1.5rem" },
  card: { background: "#1e293b", borderRadius: "12px", padding: "1.75rem", border: "1px solid #334155", cursor: "pointer", transition: "all 0.3s" },
  cardTitle: { fontSize: "1.2rem", fontWeight: "700", marginBottom: "0.75rem" },
  cardDesc: { color: "#cbd5e1", fontSize: "0.95rem", marginBottom: "1rem", lineHeight: "1.6" },
  cardContext: { background: "#0f172a", borderRadius: "8px", padding: "1rem", marginBottom: "1rem", borderLeft: "3px solid #3b82f6" },
  contextLabel: { color: "#94a3b8", fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "0.35rem", fontWeight: "600" },
  contextText: { color: "#cbd5e1", fontSize: "0.9rem", lineHeight: "1.5" },

  cardFooter: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  badge: { fontSize: "0.75rem", padding: "0.35rem 0.75rem", borderRadius: "999px", fontWeight: "600" },
  startBtn: { background: "#3b82f6", color: "#fff", border: "none", padding: "0.5rem 1.25rem", borderRadius: "6px", fontWeight: "600", fontSize: "0.85rem", cursor: "pointer", transition: "background 0.2s" },

  emptyState: { color: "#94a3b8", textAlign: "center", padding: "3rem", fontSize: "1.1rem" },
};

export default function Projects() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

    axios.get("/api/projects", config).then((r) => {
      setProjects(r.data);
      setLoading(false);
    });
  }, []);

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>🛠️ Real-World Projects</h1>
        <p style={s.subtitle}>Learn by building. Apply your skills to real scenarios.</p>
      </div>

      {loading ? (
        <div style={s.emptyState}>Loading projects...</div>
      ) : projects.length === 0 ? (
        <div style={s.emptyState}>No projects available yet.</div>
      ) : (
        <div style={s.grid}>
          {projects.map((project) => {
            const pct = project.exercise_count ? Math.round((project.completed_count / project.exercise_count) * 100) : 0;
            const diffColor = s.difficultyBadge[project.difficulty] || s.difficultyBadge.beginner;

            return (
              <div
                key={project.id}
                style={{
                  ...s.card,
                  borderColor: pct === 100 ? "#22c55e" : "#334155",
                }}
                onClick={() => navigate(`/projects/${project.id}`)}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = "#3b82f6";
                  e.currentTarget.style.boxShadow = "0 0 20px rgba(59, 130, 246, 0.1)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = pct === 100 ? "#22c55e" : "#334155";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <div style={s.cardTitle}>{project.order}. {project.title}</div>
                <div style={s.cardDesc}>{project.description}</div>

                {project.real_world_context && (
                  <div style={s.cardContext}>
                    <div style={s.contextLabel}>💡 Why This Matters</div>
                    <div style={s.contextText}>
                      {project.real_world_context}
                    </div>
                  </div>
                )}

                {/* Progress Bar */}
                <div style={{ background: "#0f172a", borderRadius: "8px", height: "6px", marginBottom: "1rem", overflow: "hidden" }}>
                  <div style={{ height: "100%", background: `linear-gradient(90deg, #3b82f6, #60a5fa)`, width: `${pct}%`, transition: "width 0.3s" }} />
                </div>

                <div style={s.cardFooter}>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    <span style={{ ...s.badge, ...diffColor }}>
                      {project.difficulty.charAt(0).toUpperCase() + project.difficulty.slice(1)}
                    </span>
                    <span style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
                      {project.completed_count}/{project.exercise_count} steps
                    </span>
                  </div>
                  <button
                    style={s.startBtn}
                    onMouseOver={(e) => (e.target.style.background = "#1d4ed8")}
                    onMouseOut={(e) => (e.target.style.background = "#3b82f6")}
                  >
                    {pct === 100 ? "Review" : pct > 0 ? "Continue" : "Start"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
