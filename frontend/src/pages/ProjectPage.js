import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

const s = {
  page: { maxWidth: "1200px", margin: "0 auto", padding: "2rem" },
  header: { marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: "1.75rem", fontWeight: "700" },
  backBtn: { background: "#1e293b", border: "1px solid #334155", color: "#cbd5e1", padding: "0.5rem 1rem", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem" },

  container: { display: "grid", gridTemplateColumns: "300px 1fr", gap: "2rem" },

  // Sidebar
  sidebar: { background: "#0f172a", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155", height: "fit-content" },
  sidebarTitle: { fontSize: "0.95rem", fontWeight: "700", marginBottom: "1rem", textTransform: "uppercase", color: "#94a3b8" },
  exerciseList: { display: "flex", flexDirection: "column", gap: "0.5rem" },
  exerciseItem: { padding: "0.75rem", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem", border: "1px solid transparent", transition: "all 0.2s" },
  exerciseItemActive: { background: "#3b82f6", color: "#fff", borderColor: "#3b82f6" },
  exerciseItemDone: { background: "#052e16", color: "#4ade80", borderColor: "#22c55e" },

  // Main content
  content: {},
  exerciseTitle: { fontSize: "1.4rem", fontWeight: "700", marginBottom: "1rem" },
  description: { color: "#cbd5e1", fontSize: "0.95rem", lineHeight: "1.7", marginBottom: "1.5rem", whiteSpace: "pre-wrap" },

  codeSection: { background: "#0f172a", borderRadius: "12px", padding: "1.5rem", marginBottom: "1.5rem", border: "1px solid #334155" },
  codeLabel: { fontSize: "0.85rem", fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", marginBottom: "0.75rem" },
  codeEditor: { background: "#1e293b", borderRadius: "8px", padding: "1rem", fontFamily: "monospace", fontSize: "0.9rem", border: "1px solid #334155", color: "#e2e8f0", minHeight: "300px", resize: "vertical", marginBottom: "1rem" },
  hint: { background: "#4d2e3b", borderLeft: "3px solid #f472b6", padding: "1rem", borderRadius: "6px", marginBottom: "1rem", color: "#fda4af" },

  footer: { display: "flex", gap: "1rem", justifyContent: "space-between", marginTop: "1.5rem" },
  btn: { padding: "0.75rem 1.5rem", borderRadius: "6px", fontWeight: "600", border: "none", cursor: "pointer", fontSize: "0.95rem" },
  btnPrimary: { background: "#3b82f6", color: "#fff" },
  btnSecondary: { background: "#1e293b", color: "#cbd5e1", border: "1px solid #334155" },

  outputSection: { background: "#0f172a", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155", marginTop: "1.5rem" },
  outputTitle: { fontSize: "0.9rem", fontWeight: "700", color: "#94a3b8", marginBottom: "1rem", textTransform: "uppercase" },
  outputBox: { background: "#1e293b", borderRadius: "6px", padding: "1rem", fontFamily: "monospace", fontSize: "0.85rem", color: "#e2e8f0", maxHeight: "300px", overflow: "auto" },
  outputError: { color: "#fca5a5" },
  outputSuccess: { color: "#4ade80" },
};

export default function ProjectPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [showHint, setShowHint] = useState(false);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem("token");
  const config = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    axios.get(`/api/projects/${projectId}`, config).then((r) => {
      setProject(r.data);
      setCode(r.data.exercises[0]?.starter_code || "");
      setLoading(false);
    });
  }, [projectId]);

  const handleSubmit = async () => {
    const exercise = project.exercises[currentExerciseIndex];
    const response = await axios.post(
      `/api/projects/${projectId}/exercises/${exercise.id}/submit`,
      { code },
      config
    );
    setResult(response.data);
  };

  if (loading || !project) return <div style={s.page}>Loading...</div>;

  const exercise = project.exercises[currentExerciseIndex];

  return (
    <div style={s.page}>
      <div style={s.header}>
        <div>
          <h1 style={s.title}>{project.title}</h1>
          <p style={{ color: "#94a3b8", marginTop: "0.25rem" }}>
            Step {currentExerciseIndex + 1} of {project.exercises.length}
          </p>
        </div>
        <button style={s.backBtn} onClick={() => navigate("/projects")}>← Projects</button>
      </div>

      <div style={s.container}>
        {/* Sidebar */}
        <div style={s.sidebar}>
          <div style={s.sidebarTitle}>Project Steps</div>
          <div style={s.exerciseList}>
            {project.exercises.map((ex, idx) => (
              <div
                key={ex.id}
                style={{
                  ...s.exerciseItem,
                  ...(idx === currentExerciseIndex ? s.exerciseItemActive : {}),
                  ...(idx < currentExerciseIndex ? s.exerciseItemDone : {}),
                }}
                onClick={() => {
                  setCurrentExerciseIndex(idx);
                  setCode(ex.starter_code);
                  setResult(null);
                  setShowHint(false);
                }}
              >
                {idx < currentExerciseIndex ? "✅ " : ""}
                {ex.title}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div style={s.content}>
          <h2 style={s.exerciseTitle}>{exercise.title}</h2>
          <p style={s.description}>{exercise.description}</p>

          {/* Code Editor */}
          <div style={s.codeSection}>
            <div style={s.codeLabel}>Your Code</div>
            <textarea
              style={s.codeEditor}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Write your Python code here..."
            />
            <button
              style={{ ...s.btn, ...s.btnPrimary }}
              onClick={handleSubmit}
            >
              Run Code
            </button>
          </div>

          {/* Hint */}
          {exercise.hint && (
            <>
              <button
                style={{ ...s.btn, ...s.btnSecondary }}
                onClick={() => setShowHint(!showHint)}
              >
                {showHint ? "Hide Hint" : "Show Hint"}
              </button>
              {showHint && (
                <div style={s.hint}>
                  <strong>Hint:</strong> {exercise.hint}
                </div>
              )}
            </>
          )}

          {/* Output */}
          {result && (
            <div style={s.outputSection}>
              <div style={s.outputTitle}>Output</div>
              <div style={s.outputBox}>
                {result.stderr && <div style={s.outputError}>{result.stderr}</div>}
                {result.stdout && <div style={s.outputSuccess}>{result.stdout}</div>}
                {result.code === 0 && result.stdout === "" && (
                  <div style={s.outputSuccess}>✅ Code executed successfully!</div>
                )}
              </div>

              {result.code === 0 && (
                <div style={{ marginTop: "1rem" }}>
                  {currentExerciseIndex < project.exercises.length - 1 ? (
                    <button
                      style={{ ...s.btn, ...s.btnPrimary }}
                      onClick={() => {
                        setCurrentExerciseIndex(currentExerciseIndex + 1);
                        setCode(project.exercises[currentExerciseIndex + 1].starter_code);
                        setResult(null);
                      }}
                    >
                      Next Step →
                    </button>
                  ) : (
                    <div style={{ color: "#4ade80", fontWeight: "700" }}>
                      🎉 Project Complete! Great job!
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
