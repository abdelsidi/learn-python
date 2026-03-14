import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const s = {
  page: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "calc(100vh - 60px)" },
  card: { background: "#1e293b", padding: "2.5rem", borderRadius: "12px", width: "100%", maxWidth: "420px", border: "1px solid #334155" },
  title: { fontSize: "1.75rem", fontWeight: "700", marginBottom: "0.5rem" },
  subtitle: { color: "#94a3b8", marginBottom: "2rem" },
  label: { display: "block", marginBottom: "0.4rem", color: "#94a3b8", fontSize: "0.9rem" },
  input: { width: "100%", padding: "0.65rem 0.9rem", background: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "#f1f5f9", fontSize: "1rem", marginBottom: "1.25rem" },
  btn: { width: "100%", padding: "0.75rem", background: "#3b82f6", color: "#fff", border: "none", borderRadius: "8px", fontWeight: "700", fontSize: "1rem", marginTop: "0.5rem" },
  error: { background: "#450a0a", color: "#fca5a5", padding: "0.75rem", borderRadius: "6px", marginBottom: "1rem", fontSize: "0.9rem" },
  footer: { marginTop: "1.5rem", textAlign: "center", color: "#94a3b8", fontSize: "0.9rem" },
};

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        <h1 style={s.title}>Welcome back</h1>
        <p style={s.subtitle}>Sign in to continue learning</p>
        {error && <div style={s.error}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <label style={s.label}>Email</label>
          <input style={s.input} type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <label style={s.label}>Password</label>
          <input style={s.input} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <button style={s.btn} type="submit" disabled={loading}>{loading ? "Signing in..." : "Sign In"}</button>
        </form>
        <div style={s.footer}>
          Don't have an account? <Link to="/register">Sign up</Link>
        </div>
      </div>
    </div>
  );
}
