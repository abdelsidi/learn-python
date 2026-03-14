import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const s = {
  page: { maxWidth: "1400px", margin: "0 auto", padding: "2rem" },
  header: { marginBottom: "2.5rem" },
  title: { fontSize: "2rem", fontWeight: "700", marginBottom: "0.5rem" },
  subtitle: { color: "#94a3b8", fontSize: "1rem" },

  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "2rem", marginBottom: "3rem" },

  // Course Card
  courseCard: { background: "#1e293b", borderRadius: "12px", overflow: "hidden", border: "1px solid #334155", cursor: "pointer", transition: "all 0.3s", display: "flex", flexDirection: "column" },
  courseHeader: { padding: "2rem 1.5rem 1rem", background: "linear-gradient(135deg, #3b82f6 0%, #1e293b 100%)" },
  courseIcon: { fontSize: "3rem", marginBottom: "0.5rem" },
  courseTitle: { fontSize: "1.3rem", fontWeight: "700", marginBottom: "0.25rem" },
  courseLevel: { display: "inline-block", padding: "0.25rem 0.75rem", borderRadius: "999px", fontSize: "0.75rem", fontWeight: "600", marginBottom: "1rem" },

  courseBody: { padding: "1.5rem", flex: 1, display: "flex", flexDirection: "column" },
  courseDesc: { color: "#cbd5e1", fontSize: "0.95rem", marginBottom: "1rem", lineHeight: "1.6", flex: 1 },
  courseMeta: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem", fontSize: "0.9rem" },
  metaItem: { background: "#0f172a", padding: "0.75rem", borderRadius: "6px", textAlign: "center" },
  metaNumber: { fontSize: "1.3rem", fontWeight: "700", color: "#3b82f6" },
  metaLabel: { color: "#94a3b8", fontSize: "0.8rem", marginTop: "0.25rem" },

  progressBar: { background: "#0f172a", borderRadius: "6px", height: "8px", marginBottom: "1rem", overflow: "hidden" },
  progressFill: { height: "100%", background: "linear-gradient(90deg, #3b82f6, #60a5fa)", transition: "width 0.3s" },

  startBtn: { background: "#3b82f6", color: "#fff", border: "none", padding: "0.6rem 1.25rem", borderRadius: "6px", fontWeight: "600", cursor: "pointer", fontSize: "0.95rem", transition: "background 0.2s" },

  // Curriculum View
  curriculumSection: { background: "#1e293b", borderRadius: "12px", padding: "2rem", border: "1px solid #334155", marginBottom: "2rem" },
  curriculumTitle: { fontSize: "1.4rem", fontWeight: "700", marginBottom: "1.5rem" },
  lessonFlow: { display: "flex", flexWrap: "wrap", gap: "1rem", alignItems: "center" },
  lessonNode: { display: "flex", alignItems: "center", gap: "0.5rem" },
  lessonCard: { background: "#0f172a", border: "2px solid #334155", borderRadius: "8px", padding: "0.75rem 1.25rem", fontSize: "0.9rem", fontWeight: "600", minWidth: "140px", textAlign: "center", transition: "all 0.2s" },
  lessonCompleted: { borderColor: "#22c55e", background: "#052e16", color: "#4ade80" },
  lessonInProgress: { borderColor: "#3b82f6", background: "#1e3a5f", color: "#60a5fa" },
  arrow: { color: "#94a3b8", fontSize: "1.5rem" },

  emptyState: { color: "#94a3b8", textAlign: "center", padding: "3rem", fontSize: "1.1rem" },
};

export default function Courses() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

    axios.get("/api/lessons", config).then((r) => {
      setLessons(r.data);
      setLoading(false);
    });
  }, []);

  // Group lessons into courses
  const courses = [
    {
      id: "fundamentals",
      title: "Python Fundamentals",
      icon: "🐍",
      description: "Master the core concepts of Python programming",
      level: "Beginner",
      levelColor: "#10b981",
      lessonIds: [1, 2, 3, 4],
    },
    {
      id: "intermediate",
      title: "Intermediate Python",
      icon: "⚙️",
      description: "Advanced data structures, OOP, and functional programming",
      level: "Intermediate",
      levelColor: "#f59e0b",
      lessonIds: [5, 6, 7, 8, 9],
    },
    {
      id: "advanced",
      title: "Advanced Python",
      icon: "🚀",
      description: "Decorators, generators, context managers, and performance",
      level: "Advanced",
      levelColor: "#ef4444",
      lessonIds: [10, 11, 12, 13],
    },
    {
      id: "libraries",
      title: "Data Science & APIs",
      icon: "📊",
      description: "NumPy, Pandas, Requests, BeautifulSoup for real-world apps",
      level: "Intermediate",
      levelColor: "#f59e0b",
      lessonIds: [14, 15, 16, 17],
    },
  ];

  const getCourseStats = (lessonIds) => {
    const courseLessons = lessons.filter(l => lessonIds.includes(l.order));
    const totalExercises = courseLessons.reduce((sum, l) => sum + (l.exercise_count || 0), 0);
    const completedExercises = courseLessons.reduce((sum, l) => sum + (l.completed_count || 0), 0);
    return { total: totalExercises, completed: completedExercises, percentage: totalExercises ? Math.round((completedExercises / totalExercises) * 100) : 0 };
  };

  if (loading) return <div style={s.page}>Loading courses...</div>;

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>📚 Python Learning Courses</h1>
        <p style={s.subtitle}>Choose a course path and master Python step by step</p>
      </div>

      {/* Course Cards */}
      <div style={s.grid}>
        {courses.map((course) => {
          const stats = getCourseStats(course.lessonIds);
          const courseLessons = lessons.filter(l => course.lessonIds.includes(l.order));

          return (
            <div
              key={course.id}
              style={s.courseCard}
              onMouseOver={(e) => {
                e.currentTarget.style.borderColor = "#3b82f6";
                e.currentTarget.style.boxShadow = "0 0 20px rgba(59, 130, 246, 0.2)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.borderColor = "#334155";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              <div style={s.courseHeader}>
                <div style={s.courseIcon}>{course.icon}</div>
                <div style={s.courseTitle}>{course.title}</div>
                <span style={{ ...s.courseLevel, background: course.levelColor + "20", color: course.levelColor }}>
                  {course.level}
                </span>
              </div>

              <div style={s.courseBody}>
                <p style={s.courseDesc}>{course.description}</p>

                <div style={s.courseMeta}>
                  <div style={s.metaItem}>
                    <div style={s.metaNumber}>{courseLessons.length}</div>
                    <div style={s.metaLabel}>Lessons</div>
                  </div>
                  <div style={s.metaItem}>
                    <div style={s.metaNumber}>{stats.total}</div>
                    <div style={s.metaLabel}>Exercises</div>
                  </div>
                </div>

                <div style={s.progressBar}>
                  <div style={{ ...s.progressFill, width: `${stats.percentage}%` }} />
                </div>
                <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1rem" }}>
                  {stats.percentage}% complete ({stats.completed}/{stats.total})
                </p>

                <button
                  style={s.startBtn}
                  onMouseOver={(e) => (e.target.style.background = "#1d4ed8")}
                  onMouseOut={(e) => (e.target.style.background = "#3b82f6")}
                  onClick={() => navigate(`/lessons/${courseLessons[0]?.id}`)}
                >
                  {stats.percentage > 0 ? "Continue" : "Start"} Course
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Curriculum Maps */}
      <div>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", marginBottom: "2rem" }}>📖 Curriculum Map</h2>

        {courses.map((course) => {
          const courseLessons = lessons.filter(l => course.lessonIds.includes(l.order)).sort((a, b) => a.order - b.order);

          return (
            <div key={course.id} style={s.curriculumSection}>
              <div style={s.curriculumTitle}>{course.title}</div>
              <div style={s.lessonFlow}>
                {courseLessons.map((lesson, idx) => {
                  const isCompleted = lesson.completed_count === lesson.exercise_count;
                  const isInProgress = lesson.completed_count > 0 && lesson.completed_count < lesson.exercise_count;

                  return (
                    <React.Fragment key={lesson.id}>
                      <div style={s.lessonNode}>
                        <div
                          style={{
                            ...s.lessonCard,
                            ...(isCompleted ? s.lessonCompleted : isInProgress ? s.lessonInProgress : {}),
                          }}
                          onClick={() => navigate(`/lessons/${lesson.id}`)}
                          title={lesson.title}
                        >
                          {isCompleted ? "✓" : isInProgress ? "→" : ""} {lesson.order}
                        </div>
                      </div>
                      {idx < courseLessons.length - 1 && <div style={s.arrow}>→</div>}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
