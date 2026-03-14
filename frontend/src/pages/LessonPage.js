import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Editor from "@monaco-editor/react";
import axios from "axios";

const s = {
  page: { display: "flex", height: "calc(100vh - 60px)" },
  sidebar: { width: "280px", background: "#1e293b", borderRight: "1px solid #334155", overflowY: "auto", padding: "1rem" },
  sidebarTitle: { fontWeight: "700", marginBottom: "1rem", color: "#f1f5f9" },
  exItem: { padding: "0.6rem 0.75rem", borderRadius: "6px", cursor: "pointer", marginBottom: "0.25rem", fontSize: "0.9rem", display: "flex", alignItems: "center", gap: "0.5rem" },
  main: { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" },
  topBar: { background: "#1e293b", padding: "1rem 1.5rem", borderBottom: "1px solid #334155" },
  exTitle: { fontWeight: "700", fontSize: "1.1rem", marginBottom: "0.25rem" },
  desc: { color: "#94a3b8", fontSize: "0.9rem", lineHeight: "1.6" },
  editorArea: { flex: 1, display: "flex", overflow: "hidden" },
  editorWrap: { flex: 1, display: "flex", flexDirection: "column" },
  editorHeader: { background: "#0f172a", padding: "0.5rem 1rem", display: "flex", gap: "0.75rem", borderBottom: "1px solid #334155" },
  runBtn: { background: "#22c55e", color: "#fff", border: "none", padding: "0.4rem 1.25rem", borderRadius: "6px", fontWeight: "600", fontSize: "0.9rem" },
  submitBtn: { background: "#3b82f6", color: "#fff", border: "none", padding: "0.4rem 1.25rem", borderRadius: "6px", fontWeight: "600", fontSize: "0.9rem" },
  hintBtn: { background: "transparent", color: "#f59e0b", border: "1px solid #f59e0b", padding: "0.4rem 1rem", borderRadius: "6px", fontSize: "0.9rem" },
  output: { width: "320px", background: "#0f172a", borderLeft: "1px solid #334155", display: "flex", flexDirection: "column" },
  outputHeader: { padding: "0.5rem 1rem", background: "#1e293b", borderBottom: "1px solid #334155", fontWeight: "600", fontSize: "0.85rem", color: "#94a3b8" },
  outputBody: { flex: 1, padding: "1rem", fontFamily: "monospace", fontSize: "0.85rem", whiteSpace: "pre-wrap", overflowY: "auto" },
  passed: { background: "#052e16", color: "#4ade80", padding: "0.75rem", margin: "0.75rem", borderRadius: "6px", fontSize: "0.85rem" },
  failed: { background: "#450a0a", color: "#fca5a5", padding: "0.75rem", margin: "0.75rem", borderRadius: "6px", fontSize: "0.85rem" },
  hint: { background: "#1c1917", color: "#fbbf24", padding: "0.75rem", margin: "0.75rem", borderRadius: "6px", fontSize: "0.85rem" },
};

export default function LessonPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [currentEx, setCurrentEx] = useState(0);
  const [code, setCode] = useState("");
  const [output, setOutput] = useState(null);
  const [submitResult, setSubmitResult] = useState(null);
  const [showHint, setShowHint] = useState(false);
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    axios.get(`/api/lessons/${id}`).then((res) => {
      setLesson(res.data);
      setCode(res.data.exercises[0]?.starter_code || "");
    });
  }, [id]);

  const exercise = lesson?.exercises[currentEx];

  const selectExercise = (idx) => {
    setCurrentEx(idx);
    setCode(lesson.exercises[idx].starter_code || "");
    setOutput(null);
    setSubmitResult(null);
    setShowHint(false);
  };

  const runCode = async () => {
    setRunning(true);
    setOutput(null);
    setSubmitResult(null);
    try {
      const res = await axios.post("/api/run", { code });
      setOutput(res.data);
    } catch {
      setOutput({ stderr: "Failed to run code.", stdout: "", code: 1 });
    } finally {
      setRunning(false);
    }
  };

  const submitCode = async () => {
    setSubmitting(true);
    setSubmitResult(null);
    try {
      const res = await axios.post(`/api/submit/${exercise.id}`, { code });
      setSubmitResult(res.data);
      if (res.data.passed) {
        setLesson((prev) => ({
          ...prev,
          exercises: prev.exercises.map((e, i) =>
            i === currentEx ? { ...e, completed: true } : e
          ),
        }));
      }
    } catch {
      setSubmitResult({ passed: false, feedback: "Submission failed." });
    } finally {
      setSubmitting(false);
    }
  };

  if (!lesson) return <div style={{ padding: "2rem" }}>Loading...</div>;

  return (
    <div style={s.page}>
      {/* Sidebar */}
      <div style={s.sidebar}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
          <button onClick={() => navigate("/dashboard")} style={{ background: "none", border: "none", color: "#60a5fa", cursor: "pointer", fontSize: "0.85rem" }}>← Back</button>
        </div>
        <div style={s.sidebarTitle}>{lesson.title}</div>
        {lesson.exercises.map((ex, i) => (
          <div
            key={ex.id}
            style={{
              ...s.exItem,
              background: i === currentEx ? "#334155" : "transparent",
              color: ex.completed ? "#4ade80" : "#e2e8f0",
            }}
            onClick={() => selectExercise(i)}
          >
            <span>{ex.completed ? "✓" : `${i + 1}.`}</span>
            <span>{ex.title}</span>
          </div>
        ))}
      </div>

      {/* Main area */}
      <div style={s.main}>
        <div style={s.topBar}>
          <div style={s.exTitle}>{exercise?.title}</div>
          <div style={s.desc}>{exercise?.description}</div>
        </div>

        <div style={s.editorArea}>
          <div style={s.editorWrap}>
            <div style={s.editorHeader}>
              <button style={s.runBtn} onClick={runCode} disabled={running}>
                {running ? "Running..." : "Run"}
              </button>
              <button style={s.submitBtn} onClick={submitCode} disabled={submitting}>
                {submitting ? "Checking..." : "Submit"}
              </button>
              {exercise?.hint && (
                <button style={s.hintBtn} onClick={() => setShowHint(!showHint)}>
                  {showHint ? "Hide Hint" : "Hint"}
                </button>
              )}
            </div>
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(val) => setCode(val || "")}
              options={{ fontSize: 14, minimap: { enabled: false }, scrollBeyondLastLine: false }}
            />
          </div>

          {/* Output panel */}
          <div style={s.output}>
            <div style={s.outputHeader}>Output</div>
            {showHint && <div style={s.hint}><strong>Hint:</strong> {exercise?.hint}</div>}
            {submitResult && (
              <div style={submitResult.passed ? s.passed : s.failed}>
                {submitResult.feedback}
              </div>
            )}
            <div style={s.outputBody}>
              {output ? (
                <>
                  {output.stdout && <span style={{ color: "#e2e8f0" }}>{output.stdout}</span>}
                  {output.stderr && <span style={{ color: "#fca5a5" }}>{output.stderr}</span>}
                  {!output.stdout && !output.stderr && <span style={{ color: "#94a3b8" }}>No output</span>}
                </>
              ) : (
                <span style={{ color: "#475569" }}>Click Run or Submit to see output...</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
