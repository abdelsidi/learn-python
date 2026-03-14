import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { translations } from "../translations";

const t = (key, lang) => {
  const keys = key.split(".");
  let value = translations[lang] || translations.en;
  for (let k of keys) {
    value = value[k];
    if (!value) return key;
  }
  return value;
};

const s = {
  page: { maxWidth: "1200px", margin: "0 auto", padding: "2rem" },
  header: { marginBottom: "2rem" },
  title: { fontSize: "1.75rem", fontWeight: "700", marginBottom: "0.25rem" },
  subtitle: { color: "#94a3b8" },

  // Stats section
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2.5rem" },
  statCard: { background: "#1e293b", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155" },
  statValue: { fontSize: "2rem", fontWeight: "700", color: "#3b82f6" },
  statLabel: { color: "#94a3b8", fontSize: "0.9rem", marginTop: "0.5rem" },

  // Progress section
  progressContainer: { marginBottom: "2.5rem" },
  progressLabel: { fontSize: "0.9rem", color: "#94a3b8", marginBottom: "0.5rem", display: "flex", justifyContent: "space-between" },
  progressBar: { background: "#1e293b", borderRadius: "8px", height: "10px", overflow: "hidden" },
  progressFill: { height: "100%", background: "linear-gradient(90deg, #3b82f6, #60a5fa)", borderRadius: "8px", transition: "width 0.5s" },

  // Grid
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1.25rem" },
  card: { background: "#1e293b", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155", cursor: "pointer", transition: "all 0.2s", position: "relative" },
  cardHover: { borderColor: "#3b82f6", boxShadow: "0 0 20px rgba(59, 130, 246, 0.1)" },
  cardTitle: { fontWeight: "700", marginBottom: "0.35rem", fontSize: "1.05rem" },
  cardDesc: { color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1rem", lineHeight: "1.5", height: "2.5rem" },
  cardFooter: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  badge: { fontSize: "0.75rem", padding: "0.2rem 0.6rem", borderRadius: "999px", fontWeight: "600" },
  startBtn: { background: "#3b82f6", color: "#fff", border: "none", padding: "0.4rem 1rem", borderRadius: "6px", fontWeight: "600", fontSize: "0.85rem", cursor: "pointer", transition: "background 0.2s" },

  // Section title
  sectionTitle: { fontSize: "1.2rem", fontWeight: "700", marginBottom: "1.25rem", marginTop: "2rem" },

  // Empty state
  emptyState: { color: "#94a3b8", textAlign: "center", padding: "2rem" },
};

export default function Dashboard() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState({ total: 0, completed: 0 });
  const [streak, setStreak] = useState({ current_streak: 0, longest_streak: 0 });
  const [achievements, setAchievements] = useState([]);
  const [hoveredLesson, setHoveredLesson] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

    axios.get("/api/lessons", config).then((r) => setLessons(r.data));
    axios.get("/api/progress", config).then((r) => setProgress(r.data));
    axios.get("/api/streak", config).then((r) => setStreak(r.data));
    axios.get("/api/achievements", config).then((r) => setAchievements(r.data));
    axios.post("/api/streak/update", {}, config);  // Update streak on visit
  }, []);

  const pct = progress.total ? Math.round((progress.completed / progress.total) * 100) : 0;
  const completedLessons = lessons.filter(l => l.completed_count === l.exercise_count).length;
  const inProgressLessons = lessons.filter(l => l.completed_count > 0 && l.completed_count < l.exercise_count).length;

  // Find next lesson to continue
  const nextLesson = lessons.find(l => l.completed_count > 0 && l.completed_count < l.exercise_count) || lessons.find(l => l.completed_count === 0);

  return (
    <div style={s.page}>
      {/* Header */}
      <div style={s.header}>
        <h1 style={s.title}>Welcome back, {user?.username || "Learner"}! 🎓</h1>
        <p style={s.subtitle}>Keep learning, keep growing.</p>
      </div>

      {/* Stats Section */}
      <div style={s.statsGrid}>
        <div style={s.statCard}>
          <div style={s.statValue}>{progress.completed}</div>
          <div style={s.statLabel}>Exercises Completed</div>
        </div>
        <div style={s.statCard}>
          <div style={s.statValue}>{completedLessons}</div>
          <div style={s.statLabel}>Lessons Mastered</div>
        </div>
        <div style={s.statCard}>
          <div style={{ ...s.statValue, color: "#ec4899" }}>🔥 {streak.current_streak}</div>
          <div style={s.statLabel}>Current Streak</div>
        </div>
        <div style={s.statCard}>
          <div style={{ ...s.statValue, color: "#f59e0b" }}>{pct}%</div>
          <div style={s.statLabel}>Overall Progress</div>
        </div>
      </div>

      {/* Overall Progress */}
      <div style={s.progressContainer}>
        <div style={s.progressLabel}>
          <span>Overall Progress</span>
          <span style={{ fontWeight: "600" }}>{progress.completed} / {progress.total} exercises</span>
        </div>
        <div style={s.progressBar}>
          <div style={{ ...s.progressFill, width: `${pct}%` }} />
        </div>
      </div>

      {/* Recommended Next Lesson */}
      {nextLesson && (
        <>
          <h2 style={s.sectionTitle}>📚 Continue Learning</h2>
          <div
            style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #1e293b 100%)",
              borderRadius: "12px",
              padding: "2rem",
              border: "1px solid #334155",
              marginBottom: "2.5rem",
              cursor: "pointer",
            }}
            onClick={() => navigate(`/lessons/${nextLesson.id}`)}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: "1.3rem", fontWeight: "700", marginBottom: "0.5rem" }}>
                  {nextLesson.order}. {nextLesson.title}
                </div>
                <div style={{ color: "#cbd5e1", fontSize: "0.95rem", marginBottom: "1rem", maxWidth: "600px" }}>
                  {nextLesson.description?.substring(0, 150)}...
                </div>
                <div style={{ fontSize: "0.9rem", color: "#94a3b8" }}>
                  {nextLesson.completed_count > 0
                    ? `${nextLesson.exercise_count - nextLesson.completed_count} exercises left`
                    : `${nextLesson.exercise_count} exercises`}
                </div>
              </div>
              <button
                style={{
                  ...s.startBtn,
                  background: "#fff",
                  color: "#3b82f6",
                  padding: "0.6rem 1.5rem",
                  fontSize: "0.95rem",
                }}
              >
                {nextLesson.completed_count > 0 ? "Continue" : "Start"}
              </button>
            </div>
          </div>
        </>
      )}

      {/* Achievements/Badges */}
      {achievements.length > 0 && (
        <>
          <h2 style={s.sectionTitle}>🏆 Your Achievements</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: "1rem", marginBottom: "2.5rem" }}>
            {achievements.map((badge) => (
              <div
                key={badge.badge_id}
                style={{
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "12px",
                  padding: "1.25rem",
                  textAlign: "center",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                title={badge.description}
              >
                <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>{badge.badge_icon}</div>
                <div style={{ fontSize: "0.85rem", fontWeight: "600", marginBottom: "0.25rem" }}>
                  {badge.badge_name}
                </div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>
                  {new Date(badge.unlocked_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* All Lessons */}
      <h2 style={s.sectionTitle}>📖 All Lessons</h2>
      {lessons.length === 0 ? (
        <div style={s.emptyState}>Loading lessons...</div>
      ) : (
        <div style={s.grid}>
          {lessons.map((lesson) => {
            const done = lesson.completed_count === lesson.exercise_count;
            const started = lesson.completed_count > 0;
            const lessonPct = lesson.exercise_count ? Math.round((lesson.completed_count / lesson.exercise_count) * 100) : 0;

            return (
              <div
                key={lesson.id}
                style={{
                  ...s.card,
                  ...(hoveredLesson === lesson.id ? s.cardHover : {}),
                  borderColor: done ? "#22c55e" : started ? "#3b82f6" : "#334155",
                }}
                onMouseEnter={() => setHoveredLesson(lesson.id)}
                onMouseLeave={() => setHoveredLesson(null)}
                onClick={() => navigate(`/lessons/${lesson.id}`)}
              >
                {/* Status badge */}
                <div style={{ position: "absolute", top: "1rem", right: "1rem" }}>
                  {done ? (
                    <span style={{ fontSize: "1.5rem" }}>✅</span>
                  ) : started ? (
                    <span style={{ fontSize: "1.5rem" }}>⏳</span>
                  ) : (
                    <span style={{ fontSize: "1.5rem" }}>🔒</span>
                  )}
                </div>

                <div style={s.cardTitle}>{lesson.order}. {lesson.title}</div>
                <div style={s.cardDesc}>{lesson.description?.substring(0, 100)}...</div>

                {/* Mini progress bar */}
                <div style={{ ...s.progressBar, marginBottom: "0.75rem", height: "6px" }}>
                  <div style={{ ...s.progressFill, width: `${lessonPct}%` }} />
                </div>

                <div style={s.cardFooter}>
                  <span
                    style={{
                      ...s.badge,
                      background: done ? "#052e16" : started ? "#1e3a5f" : "#1e293b",
                      color: done ? "#4ade80" : started ? "#60a5fa" : "#94a3b8",
                    }}
                  >
                    {lesson.completed_count}/{lesson.exercise_count}
                  </span>
                  <button
                    style={s.startBtn}
                    onMouseOver={(e) => (e.target.style.background = "#1d4ed8")}
                    onMouseOut={(e) => (e.target.style.background = "#3b82f6")}
                  >
                    {done ? "Review" : started ? "Continue" : "Start"}
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
